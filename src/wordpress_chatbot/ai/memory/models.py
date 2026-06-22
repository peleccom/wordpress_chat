from __future__ import annotations

from typing import Any, TypedDict

PROFILE_KEY = "profile"
LEAD_KEY = "lead"


class UserProfileDocument(TypedDict):
    """Cross-thread lead profile stored under the user namespace."""

    data: dict[str, Any]
    saved_at: str


class DialogSummaryDocument(TypedDict):
    """Per-thread dialog summary stored under the thread namespace."""

    data: dict[str, Any]
    updated_at: str
    message_count: int


def get_profile_namespace(user_id: str) -> tuple[str, ...]:
    """LangGraph store namespace for a user's lead profile."""
    return ("users", user_id)


def get_summary_namespace(user_id: str, thread_id: str) -> tuple[str, ...]:
    """LangGraph store namespace for a thread's dialog summary."""
    return ("threads", user_id, thread_id)
