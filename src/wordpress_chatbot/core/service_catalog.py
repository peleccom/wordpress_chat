from __future__ import annotations

import json
from functools import cache
from pathlib import Path

_PROMPTS_DATA_DIR = Path(__file__).resolve().parent.parent / "ai" / "prompts_data"
_SERVICES_URLS_PATH = _PROMPTS_DATA_DIR / "services_urls.json"


@cache
def load_service_urls() -> dict[str, str]:
    return json.loads(_SERVICES_URLS_PATH.read_text(encoding="utf-8"))


def resolve_service_url(service_name: str) -> str | None:
    """Resolve a service page URL by exact catalog title (case-insensitive)."""
    query = service_name.strip()
    if not query:
        return None

    query_lower = query.lower()
    for title, url in load_service_urls().items():
        if title.lower() == query_lower:
            return url

    return None
