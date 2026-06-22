import json
from functools import cache
from pathlib import Path
from typing import Any

_PROMPTS_DATA_DIR = Path(__file__).resolve().parent / "prompts_data"
_MEMORY_SCHEMA_PATH = _PROMPTS_DATA_DIR / "memory_suggested_fields.json"


def prompt_path(name: str) -> Path:
    return _PROMPTS_DATA_DIR / name


@cache
def _read_prompt_file(name: str) -> str:
    path = prompt_path(name)
    return path.read_text(encoding="utf-8").strip()


def load_prompt(name: str, **kwargs: str) -> str:
    template = _read_prompt_file(name)
    return template.format(**kwargs)


def get_topic_guard_prompt() -> str:
    return load_prompt("topic_guard_prompt.md")


def get_greeting_message():
    return (
        "Hi! I'm an AI assistant for Effective Soft. I can help you learn about our "
        "case studies, services, and expertise.\n\n"
        "⚠️ Please note: I'm an AI and may make mistakes. "
        "For important matters, please contact our team directly."
    )


def get_services_prompt() -> str:
    return load_prompt(
        "services_prompt.md",
        services_catalog=load_prompt("services.md"),
    )


def load_suggested_fields_schema() -> dict[str, Any]:
    return json.loads(_MEMORY_SCHEMA_PATH.read_text(encoding="utf-8"))


def suggested_fields_reference(section: str) -> str:
    """Human-readable suggested fields for LLM prompts (not enforced)."""
    schema = load_suggested_fields_schema()[section]
    lines = [schema["description"], "Suggested fields (use when relevant; add others freely):"]
    for field, description in schema["suggested_fields"].items():
        lines.append(f"- {field}: {description}")
    return "\n".join(lines)


def get_dialog_summary_refresh_system_prompt() -> str:
    return load_prompt(
        "dialog_summary_refresh_system.md",
        suggested_fields=suggested_fields_reference("dialog_summary"),
    )


def get_dialog_summary_refresh_user_prompt(*, previous_summary_json: str, transcript: str) -> str:
    return load_prompt(
        "dialog_summary_refresh_user.md",
        previous_summary_json=previous_summary_json,
        transcript=transcript,
    )


def get_memory_context_prompt(*, memory: dict[str, Any] | None = None) -> str | None:
    if not memory:
        return None
    memory_json = json.dumps(memory, indent=2, ensure_ascii=False)
    return load_prompt("memory_context.md", memory_json=memory_json)


def get_system_prompt(
    *,
    memory: dict[str, Any] | None = None,
) -> str:
    parts = [load_prompt("system_prompt.md"), get_services_prompt()]

    memory_prompt = get_memory_context_prompt(memory=memory)
    if memory_prompt:
        parts.append(memory_prompt)

    return "\n\n".join(parts).strip()
