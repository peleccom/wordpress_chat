from __future__ import annotations

import logging
from collections.abc import Sequence

from langchain.messages import AIMessage, AnyMessage, HumanMessage

from es_website_chatbot.core.markdown import md_soup

ALLOWED_DOMAINS = ["https://www.effectivesoft.com"]
PII_EMAIL_PLACEHOLDER = "<EMAIL_ADDRESS>"

logger = logging.getLogger(__name__)

CHAINLIT_THREAD_ID_SUFFIX = "\n\nThread id: {thread_id}"

__all__ = [
    "CHAINLIT_THREAD_ID_SUFFIX",
    "PII_EMAIL_PLACEHOLDER",
    "append_chainlit_thread_id",
    "check_url_domain",
    "has_user_messages",
    "md_soup",
    "resolve_contact_email",
    "select_messages_for_topic_guard",
]


def has_user_messages(messages: list[AnyMessage]) -> bool:
    """True if the slice contains at least one non-empty user message."""
    return any(
        isinstance(message, HumanMessage) and isinstance(message.content, str) and message.content.strip()
        for message in messages
    )


def select_messages_for_topic_guard(messages: Sequence[AnyMessage], limit: int) -> list[AnyMessage]:
    """Recent user/assistant text turns safe for a standalone OpenAI chat request.

    The graph checkpoint keeps the full agent trace (tool_calls, ToolMessage, etc.).
    topic_guard sends only a short slice to a separate model call that does not continue
    tool execution. OpenAI rejects ToolMessage unless it immediately follows an assistant
    message with tool_calls; assistant messages that still carry tool_calls without their
    tool results are also unsafe in that context.

    HumanMessage is appended as-is (no tool metadata). AIMessage is recreated with text
    content only so tool_calls and other tool-round fields are not forwarded.
    """
    selected: list[AnyMessage] = []
    for message in messages:
        if isinstance(message, HumanMessage):
            if isinstance(message.content, str) and message.content.strip():
                selected.append(message)
        elif isinstance(message, AIMessage) and isinstance(message.content, str) and message.content.strip():
            # Strip tool_calls: topic guard is not resuming the agent tool loop.
            selected.append(AIMessage(content=message.content))
    return selected[-limit:]


def handle_tool_errors(error: Exception) -> str:
    # Handle tool errors. Remove sensitive data. For now, just return the error message
    logger.error(f"Error: {error!r}\n Please fix your mistakes.", exc_info=error)
    return f"Tool error: Please check your input and try again. ({error!r})"


def append_chainlit_thread_id(message: str, thread_id: str | None) -> str:
    """Append Chainlit thread id to the contact form message for CRM correlation."""
    if not thread_id:
        return message
    suffix = CHAINLIT_THREAD_ID_SUFFIX.format(thread_id=thread_id)
    if suffix in message:
        return message
    return message.rstrip() + suffix


def resolve_contact_email(user_email: str | None) -> str:
    """Email from agent state only (set by pii_guard when extracted)."""
    if user_email:
        return str(user_email)
    raise ValueError("A valid email address is required. Ask the user for their email before filling the contact form.")


def check_url_domain(url: str):
    if not any(url.startswith(domain) for domain in ALLOWED_DOMAINS):
        return False, "Error: URL not allowed. " + f"Must start with one of: {', '.join(ALLOWED_DOMAINS)}"
    return True, None
