from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, cast

from langgraph.store.base import BaseStore

from es_website_chatbot.ai.memory.models import (
    LEAD_KEY,
    PROFILE_KEY,
    DialogSummaryDocument,
    UserProfileDocument,
    get_profile_namespace,
    get_summary_namespace,
)

logger = logging.getLogger(__name__)


async def _get_document(store: BaseStore, namespace: tuple[str, ...], key: str) -> dict[str, Any] | None:
    """Load a document dict from the store, or None if missing or invalid."""
    item = await store.aget(namespace, key)
    if item is None:
        return None
    if not isinstance(item.value, dict):
        logger.warning("Invalid lead document in store for namespace %s", namespace)
        return None
    return item.value


async def _put_document(store: BaseStore, namespace: tuple[str, ...], document: dict[str, Any], key: str) -> None:
    """Write a document dict to the store under the given key."""
    await store.aput(namespace, key, document)


async def get_user_profile(store: BaseStore, user_id: str) -> UserProfileDocument | None:
    """Load the user's cross-thread lead profile."""
    document = await _get_document(store, get_profile_namespace(user_id), PROFILE_KEY)
    if document is None or "data" not in document:
        return None
    return cast(UserProfileDocument, document)


async def save_user_profile(
    store: BaseStore,
    user_id: str,
    *,
    email: str,
    extra: dict[str, Any] | None = None,
) -> UserProfileDocument:
    """Merge and persist email and optional extra profile fields."""
    existing = await get_user_profile(store, user_id)
    data = dict(existing["data"]) if existing else {}
    data["email"] = email
    if extra:
        data.update(extra)

    document: UserProfileDocument = {
        "data": data,
        "saved_at": datetime.now(UTC).isoformat(),
    }
    await _put_document(store, get_profile_namespace(user_id), cast(dict[str, Any], document), PROFILE_KEY)
    logger.info("Saved user profile memory for %s", user_id)
    return document


async def get_dialog_summary(store: BaseStore, user_id: str, thread_id: str) -> DialogSummaryDocument | None:
    """Load the per-thread dialog summary for a user."""
    document = await _get_document(store, get_summary_namespace(user_id, thread_id), LEAD_KEY)
    if document is None or "data" not in document:
        return None
    return cast(DialogSummaryDocument, document)


async def save_dialog_summary(
    store: BaseStore,
    user_id: str,
    thread_id: str,
    *,
    data: dict[str, Any],
    message_count: int,
) -> DialogSummaryDocument:
    """Persist discovery and context fields for the current thread."""
    document: DialogSummaryDocument = {
        "data": data,
        "updated_at": datetime.now(UTC).isoformat(),
        "message_count": message_count,
    }
    await _put_document(store, get_summary_namespace(user_id, thread_id), cast(dict[str, Any], document), LEAD_KEY)
    logger.info("Saved dialog summary memory for user=%s thread=%s", user_id, thread_id)
    return document
