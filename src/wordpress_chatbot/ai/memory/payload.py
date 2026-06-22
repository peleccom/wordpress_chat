from __future__ import annotations

from typing import Any

from es_website_chatbot.ai.memory.models import DialogSummaryDocument, UserProfileDocument


def profile_email(profile: UserProfileDocument | None) -> str | None:
    """Return the stored email, or None if absent."""
    if profile is None:
        return None
    email = profile["data"].get("email")
    return email if isinstance(email, str) and email else None


def build_memory_payload(
    profile: UserProfileDocument | None,
    summary: DialogSummaryDocument | None,
) -> dict[str, Any] | None:
    """Shape store documents into the payload injected into the system prompt."""
    payload: dict[str, Any] = {}
    if profile is not None:
        payload["user_profile"] = {
            **profile["data"],
            "_saved_at": profile["saved_at"],
        }
    if summary is not None:
        payload["dialog_summary"] = {
            **summary["data"],
            "_updated_at": summary["updated_at"],
            "_message_count": summary["message_count"],
        }
    if not payload:
        return None
    return payload
