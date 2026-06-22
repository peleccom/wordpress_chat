from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChatContext:
    """Runtime conext passed to the agent graph. Acessing through `runtime.context`."""

    user_id: str
