import asyncio
import logging
from typing import Any, cast

from langchain.agents import create_agent
from langchain.agents.middleware.summarization import SummarizationMiddleware
from langchain.agents.middleware.types import ModelRequest, dynamic_prompt
from langchain.chat_models import BaseChatModel
from langchain.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from langgraph.store.base import BaseStore
from presidio_anonymizer.entities import OperatorConfig
from pydantic import BaseModel as PydanticModel

from es_website_chatbot.ai.context import ChatContext
from es_website_chatbot.ai.memory import (
    build_memory_payload,
    get_dialog_summary,
    get_user_profile,
    profile_email,
    refresh_dialog_summary,
)
from es_website_chatbot.ai.middlewares import handle_tool_errors_middleware
from es_website_chatbot.ai.pii import analyzer as pii_analyzer
from es_website_chatbot.ai.pii import anonymizer as pii_anonymizer
from es_website_chatbot.ai.prompts import get_system_prompt, get_topic_guard_prompt
from es_website_chatbot.ai.state import CustomAgentState
from es_website_chatbot.ai.tools import (
    fetch_page_tool,
    fill_contact_form_tool,
    get_domains_tool,
    resolve_service_url_tool,
    retrieve_case_studies_tool,
    save_user_email_tool,
    specify_case_study_intent_tool,
)
from es_website_chatbot.ai.utils import select_messages_for_topic_guard
from es_website_chatbot.settings import settings

response_model = ChatOpenAI(
    model=settings.openai_model,
    api_key=settings.openai_api_key,
    base_url=str(settings.openai_base_url) if settings.openai_base_url else None,
    temperature=settings.openai_temperature,
)
topic_guard_model = ChatOpenAI(
    model=settings.topic_guard_model,
    api_key=settings.openai_api_key,
    base_url=str(settings.openai_base_url) if settings.openai_base_url else None,
    temperature=0,
)
summarization_model = response_model.with_config({"metadata": {"disable_streaming": True}})
memory_summary_model = response_model.with_config({"metadata": {"disable_streaming": True}})
logger = logging.getLogger(__name__)

background_tasks: set[asyncio.Task] = set()

tools = [
    get_domains_tool,
    specify_case_study_intent_tool,
    retrieve_case_studies_tool,
    save_user_email_tool,
    resolve_service_url_tool,
    fetch_page_tool,
    fill_contact_form_tool,
]


class TopicGuardResult(PydanticModel):
    is_relevant: bool
    rejection_message: str | None = None


@dynamic_prompt
async def system_prompt_middleware(request: ModelRequest) -> str:
    """Generate system prompt from DB data and long-term memory store."""
    profile = None
    summary = None

    runtime = request.runtime
    if runtime.store and isinstance(runtime.context, ChatContext):
        user_id = runtime.context.user_id
        profile = await get_user_profile(runtime.store, user_id)
        execution_info = runtime.execution_info
        thread_id = execution_info.thread_id if execution_info else None
        if thread_id:
            summary = await get_dialog_summary(runtime.store, user_id, thread_id)

    memory = build_memory_payload(profile, summary)

    return get_system_prompt(memory=memory)


def create_chat_agent(*, store: BaseStore | None = None) -> CompiledStateGraph[Any, ChatContext, Any, Any]:
    return create_agent(
        cast(BaseChatModel, response_model),
        tools=tools,
        state_schema=CustomAgentState,
        context_schema=ChatContext,
        store=store,
        middleware=cast(
            Any,
            [
                system_prompt_middleware,
                SummarizationMiddleware(
                    cast(BaseChatModel, summarization_model),
                    trigger=[
                        ("messages", settings.summarization_trigger_messages),
                    ],
                    keep=("messages", settings.summarization_keep_messages),
                ),
                handle_tool_errors_middleware,
            ],
        ),
        name="chat_agent",
    )


def pii_guard_route(state: CustomAgentState) -> str:
    return END if state.get("multiple_emails_warning") else "topic_guard"


async def pii_guard_node(state: CustomAgentState, runtime: Runtime[ChatContext]):
    last_message = state["messages"][-1]
    content = last_message.content
    if not isinstance(content, str):
        return {"multiple_emails_warning": False}

    updates: dict[str, Any] = {"multiple_emails_warning": False}

    if not (analysis := pii_analyzer.analyze(content, language="en")):
        if not state.get("user_email") and runtime.store:
            profile = await get_user_profile(runtime.store, runtime.context.user_id)
            if email := profile_email(profile):
                updates["user_email"] = email
        return updates

    email_recognizer_results = [r for r in analysis if r.entity_type == "EMAIL_ADDRESS"]

    if len(email_recognizer_results) > 1:
        return {
            "multiple_emails_warning": True,
            "messages": [
                AIMessage(
                    content=(
                        "I noticed multiple email addresses in your message. "
                        "Please provide a single email address so I can follow up with you."
                    )
                )
            ],
        }

    if email_recognizer_results:
        updates["user_email"] = content[email_recognizer_results[0].start : email_recognizer_results[0].end]
    elif not state.get("user_email") and runtime.store:
        profile = await get_user_profile(runtime.store, runtime.context.user_id)
        if email := profile_email(profile):
            updates["user_email"] = email

    anonymized = pii_anonymizer.anonymize(
        text=content,
        analyzer_results=analysis,  # ty: ignore[invalid-argument-type]
        operators={
            "PERSON": OperatorConfig("replace", {"new_value": "<THE USER>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL_ADDRESS>"}),
        },
    )
    sanitized_message = last_message.model_copy(update={"content": anonymized.text})
    return {**updates, "messages": [sanitized_message]}


def topic_guard_route(state: CustomAgentState) -> str:
    return END if state["off_topic"] else "agent"


async def topic_guard_node(state: CustomAgentState):
    last_message = state["messages"][-1]
    if not isinstance(last_message.content, str):
        return {"off_topic": False}

    history = select_messages_for_topic_guard(
        state["messages"],
        limit=settings.topic_guard_history_size,
    )
    result = cast(
        TopicGuardResult,
        await topic_guard_model.with_structured_output(TopicGuardResult).ainvoke([
            SystemMessage(content=get_topic_guard_prompt()),
            *history,
        ]),
    )

    if result.is_relevant:
        return {"off_topic": False}

    return {
        "off_topic": True,
        "messages": [AIMessage(content=result.rejection_message)],
    }


async def memory_node(state: CustomAgentState, runtime: Runtime[ChatContext]):
    if not runtime.store:
        return {}

    store = runtime.store
    execution_info = runtime.execution_info
    thread_id = execution_info.thread_id if execution_info else None
    if not thread_id:
        return {}

    messages = list(state["messages"])

    async def refresh_summary():
        try:
            await refresh_dialog_summary(
                store,
                user_id=runtime.context.user_id,
                thread_id=thread_id,
                messages=messages,
                model=cast(BaseChatModel, memory_summary_model),
            )
        except Exception:
            logger.exception("Failed to refresh dialog summary")

    task = asyncio.create_task(refresh_summary())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    return {}


def make_agent_node(chat_agent: CompiledStateGraph[Any, ChatContext, Any, Any]):
    async def agent_node(state: CustomAgentState, runtime: Runtime[ChatContext]):
        state_copy = {**state}
        del state_copy["messages"]
        logger.info("Agent state: %s", state_copy)
        logger.info("Calling agent")
        return await chat_agent.ainvoke(state, context=runtime.context)

    return agent_node


def build_graph(*, store: BaseStore | None = None) -> StateGraph[Any, ChatContext, Any, Any]:
    chat_agent = create_chat_agent(store=store)
    graph_builder = StateGraph(cast(Any, CustomAgentState), context_schema=ChatContext)
    graph_builder.add_node("pii_guard", pii_guard_node)
    graph_builder.add_node("topic_guard", topic_guard_node, metadata={"disable_streaming": True})
    graph_builder.add_node("agent", make_agent_node(chat_agent))
    graph_builder.add_node("memory", memory_node, metadata={"disable_streaming": True})

    graph_builder.add_edge(START, "pii_guard")
    graph_builder.add_conditional_edges(
        "pii_guard",
        pii_guard_route,
        {
            END: END,
            "topic_guard": "topic_guard",
        },
    )
    graph_builder.add_conditional_edges(
        "topic_guard",
        topic_guard_route,
        {
            END: END,
            "agent": "agent",
        },
    )
    graph_builder.add_edge("agent", "memory")
    graph_builder.add_edge("memory", END)

    return graph_builder
