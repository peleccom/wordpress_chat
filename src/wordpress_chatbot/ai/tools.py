import json
import logging
from datetime import timedelta

import chainlit as cl
import httpx
from cachier import cachier
from chainlit.context import get_context
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

from es_website_chatbot.ai.context import ChatContext
from es_website_chatbot.ai.memory import save_user_profile
from es_website_chatbot.ai.retrievers import retrieve
from es_website_chatbot.ai.state import (
    CaseStudyIntent,
    ContactFormFields,
    CustomAgentState,
    FillContactFormInput,
)
from es_website_chatbot.ai.utils import append_chainlit_thread_id, check_url_domain, resolve_contact_email
from es_website_chatbot.core.copilot import CopilotFunctionName
from es_website_chatbot.core.service_catalog import resolve_service_url
from es_website_chatbot.core.services import list_available_case_study_domains
from es_website_chatbot.es_site_parser.service_page import extract_service_page_content
from es_website_chatbot.infrastructure.db.case_study_store import load_case_studies
from es_website_chatbot.infrastructure.db.database import Session

logger = logging.getLogger(__name__)


def _case_study_vector_filter(intent: CaseStudyIntent | None) -> dict | None:
    """
    Since store don't support contains operator, build a filter condition with text search
    See filtering refernce: https://github.com/langchain-ai/langchain-postgres/blob/main/examples/pg_vectorstore.ipynb
    """
    if not intent:
        return None
    clauses = []
    domain = intent.domain
    if isinstance(domain, str) and domain.strip():
        clauses.append({
            "$or": [
                {"domains": {"$like": f'%"{domain.strip()}"%'}},
                {"domains": "[]"},  # Pass all with empty domains
            ]
        })
    tech_stack = intent.tech_stack
    if isinstance(tech_stack, list) and len(tech_stack) == 1:
        clauses.append({"tech_stack": {"$like": f'%"{tech_stack[0]}"%'}})
    return {"$and": clauses}


def _guard_tool_message(runtime: ToolRuntime[ChatContext, CustomAgentState], content: str) -> Command:
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=content,
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


def _require_case_study_domains(
    runtime: ToolRuntime[ChatContext, CustomAgentState],
) -> list[str] | Command:
    domains = runtime.state.get("case_study_domains") or []
    if not domains:
        return _guard_tool_message(
            runtime,
            "Call get_domains_tool first to load case study domain labels.",
        )
    return domains


def _domain_in_catalog(domain: str, catalog: list[str]) -> bool:
    domain_lower = domain.strip().lower()
    return any(label.lower() == domain_lower for label in catalog)


@tool
async def get_domains_tool(runtime: ToolRuntime[ChatContext, CustomAgentState]):
    """Load case study domain labels from the catalog.

    Call before specify_case_study_intent_tool or retrieve_case_studies_tool.
    """
    domains = await list_available_case_study_domains()
    labels_json = json.dumps(domains, ensure_ascii=False)
    logger.info("Loaded %d case study domains", len(domains))

    return Command(
        update={
            "case_study_domains": domains,
            "messages": [
                ToolMessage(
                    content=(
                        "Case study domain labels (use exactly one for domain in "
                        f"specify_case_study_intent_tool, or omit if none fit):\n{labels_json}"
                    ),
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        },
    )


@tool
async def retrieve_case_studies_tool(
    query: str,
    runtime: ToolRuntime[ChatContext, CustomAgentState],
) -> str | Command:
    """Search and return information about matching case studies.

    Prerequisites: get_domains_tool, then specify_case_study_intent_tool.

    Args:
        query: Search query. Rephrased user idea to find similar case studies
    """
    domains_guard = _require_case_study_domains(runtime)
    if isinstance(domains_guard, Command):
        return domains_guard

    if not runtime.state.get("case_study_intent"):
        return _guard_tool_message(
            runtime,
            "Call specify_case_study_intent_tool first to record retrieval intent.",
        )

    intent = runtime.state.get("case_study_intent")
    vector_filter = _case_study_vector_filter(intent)

    logger.info('Combined search: query "%s" filter=%s', query, vector_filter)
    docs = await retrieve(query)
    case_studies = []

    logger.info("Found %d search results", len(docs))

    urls = [doc.metadata["url"] for doc in docs]
    async with Session() as session:
        case_study_items = await load_case_studies(session, urls)
    logger.info("Found %d documents", len(case_study_items))
    for case_study_item in case_study_items:
        case_studies.append(
            f"""
        URL: {case_study_item.url}
        Title: {case_study_item.title}
        Description: {case_study_item.description}
        Image: {case_study_item.image}
        Domains: {", ".join(case_study_item.domains)}
        Tech stack: {", ".join(case_study_item.tech_stack)}
        Content: {case_study_item.solution}
        """.strip()
        )
    return "\n------\n".join(case_studies)


@tool
async def save_user_email_tool(runtime: ToolRuntime[ChatContext, CustomAgentState]):
    """Save information about user like email address"""
    state = runtime.state
    email = state.get("user_email")
    if email and runtime.store:
        await save_user_profile(runtime.store, runtime.context.user_id, email=email)
    return Command(
        update={
            "user_email": email,
            "messages": [
                ToolMessage(
                    content="User shared his email address.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        },
    )


@tool(args_schema=CaseStudyIntent)
def specify_case_study_intent_tool(
    domain: str | None,
    tech_stack: list[str] | None,
    runtime: ToolRuntime[ChatContext, CustomAgentState],
):
    """Save useful intent about possible case study indirectly mentioned by user.

    Prerequisites: get_domains_tool. Any value will rewrite previous value.

    Args:
        domain: Industry or business domain (exact label from get_domains_tool, or omit).
        tech_stack: List of tech stack keywords.
    """
    domains_guard = _require_case_study_domains(runtime)
    if isinstance(domains_guard, Command):
        return domains_guard

    if domain and domain.strip() and not _domain_in_catalog(domain, domains_guard):
        labels_json = json.dumps(domains_guard, ensure_ascii=False)
        return _guard_tool_message(
            runtime,
            f"domain {domain!r} is not in the catalog. Use exactly one of: {labels_json}",
        )

    logger.info(
        "Call specify_case_study_intent_tool %s %s",
        domain,
        tech_stack,
    )

    current_model = runtime.state.get("case_study_intent")

    if not current_model:
        current: dict = {}
    else:
        current = current_model.model_dump()

    current["domain"] = domain or None
    current["tech_stack"] = tech_stack or []

    updated_model = CaseStudyIntent.model_validate(current)

    logger.info("Updated case study intent: %s", updated_model)

    return Command(
        update={
            "case_study_intent": updated_model,
            "messages": [
                ToolMessage(
                    content=f"Case study information updated\n case_study_intent: {updated_model}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


@tool(args_schema=FillContactFormInput)
async def fill_contact_form_tool(
    message: str,
    runtime: ToolRuntime[ChatContext, CustomAgentState],
) -> str:
    """Pre-fill the website Contact us form (email, message) for the user to review and submit.

    Call when the user wants contact, follow-up, or to save their details — e.g. get in touch,
    discuss later, save my contact, reach out, callback.

    Before calling: ensure message is ready and a user email was captured in state. If email is
    missing, ask the user for it. Summarize the conversation for message when not stated explicitly.
    Never claim the form was submitted.
    """
    user_email = runtime.state.get("user_email")
    thread_id = runtime.execution_info.thread_id if runtime.execution_info else None
    if not thread_id:
        try:
            thread_id = get_context().session.thread_id
        except Exception:
            thread_id = None
    fields = ContactFormFields(
        email=resolve_contact_email(str(user_email) if user_email else None),
        message=append_chainlit_thread_id(message, thread_id),
    )
    logger.info("Prepared contact form for <%s>", fields.email)

    if get_context().session.client_type == "copilot":
        result = await cl.CopilotFunction(
            name=CopilotFunctionName.FILL_CONTACT_FORM,
            args=fields.model_dump(mode="json"),
        ).acall()
        if result:
            return f"Contact form pre-filled. {result}"

    return "Contact form prepared; please review and click Send message."


@tool
def resolve_service_url_tool(service_name: str) -> str:
    """Look up the EffectiveSoft service page URL for a service by name.

    Use before fetch_page_tool when you need details about a specific service.
    Pass the exact service title from the services catalog (full match only).
    """
    logger.info("Resolve service URL for %r", service_name)
    url = resolve_service_url(service_name)
    if url:
        return url
    return f"No service found matching {service_name!r}. Use an exact title from the services catalog."


@tool
@cachier(stale_after=timedelta(minutes=20))
async def fetch_page_tool(url: str) -> str:
    """Fetch and convert content from an EffectiveSoft website page URL.

    The URL must be on an allowed domain (effectivesoft.com). For catalog services,
    resolve the URL with resolve_service_url_tool when you only have a service name.
    """
    logger.info(f"Fetch data {url}")
    ok, message = check_url_domain(url)
    if not ok:
        return message

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)

    response.raise_for_status()

    try:
        _, _, content = extract_service_page_content(response.text)
    except ValueError:
        return f"Could not find main content on {url}"

    logger.info("Fetched data from %s %s", url, content)
    return content
