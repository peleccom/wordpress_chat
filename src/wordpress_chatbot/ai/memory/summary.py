from __future__ import annotations

import json
import re
from typing import Any

from langchain.chat_models import BaseChatModel
from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.store.base import BaseStore

from es_website_chatbot.ai.memory.crud import get_dialog_summary, save_dialog_summary
from es_website_chatbot.ai.memory.models import DialogSummaryDocument
from es_website_chatbot.ai.prompts import (
    get_dialog_summary_refresh_system_prompt,
    get_dialog_summary_refresh_user_prompt,
)
from es_website_chatbot.ai.utils import has_user_messages
from es_website_chatbot.settings import settings


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse LLM output into a JSON object for lead discovery storage.

    The dialog-summary refresh model returns plain text, not structured output.
    Models often wrap JSON in markdown fences despite prompt instructions, so this
    helper strips optional ``` fences before calling ``json.loads``.

    Use this instead of bare ``json.loads`` because it also ensures the top-level
    value is an object (dict), which is required for free-form ``data`` documents
    in the LangGraph store.

    Args:
        text: Raw model response (JSON object, optionally fenced).

    Returns:
        Parsed dictionary ready for ``save_dialog_summary(..., data=...)``.

    Raises:
        json.JSONDecodeError: If the content is not valid JSON after normalization.
        TypeError: If JSON parses to a non-object (e.g. array or string).
    """
    content = text.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        msg = "Lead JSON must be an object"
        raise TypeError(msg)
    return parsed


def format_messages_for_summary_transcript(messages: list[AnyMessage]) -> str:
    """Build a User/Assistant transcript for the summary refresh prompt."""
    lines: list[str] = []
    for message in messages:
        if isinstance(message, HumanMessage):
            role = "User"
        elif isinstance(message, AIMessage):
            role = "Assistant"
        else:
            continue
        content = message.content
        if isinstance(content, str) and content.strip():
            lines.append(f"{role}: {content.strip()}")
    return "\n".join(lines)


async def refresh_dialog_summary(
    store: BaseStore,
    *,
    user_id: str,
    thread_id: str,
    messages: list[AnyMessage],
    model: BaseChatModel,
) -> DialogSummaryDocument | None:
    """Refresh thread summary via LLM when enough new user messages exist."""
    if len(messages) < settings.memory_summary_min_messages:
        return None

    existing = await get_dialog_summary(store, user_id, thread_id)
    if existing and existing["message_count"] == len(messages):
        return existing

    recent_messages = messages[-settings.memory_summary_context_messages :]
    if not has_user_messages(recent_messages):
        return None

    transcript = format_messages_for_summary_transcript(recent_messages)
    if not transcript:
        return None

    previous_summary_json = json.dumps(existing["data"], indent=2) if existing else "{}"
    response = await model.ainvoke([
        SystemMessage(content=get_dialog_summary_refresh_system_prompt()),
        HumanMessage(
            content=get_dialog_summary_refresh_user_prompt(
                previous_summary_json=previous_summary_json,
                transcript=transcript,
            )
        ),
    ])
    raw = response.text if hasattr(response, "text") else str(response.content)
    summary_data = parse_json_object(raw)

    return await save_dialog_summary(
        store,
        user_id,
        thread_id,
        data=summary_data,
        message_count=len(messages),
    )
