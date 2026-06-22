import chainlit as cl
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage


@wrap_tool_call  # type: ignore[no-matching-overload]
async def handle_tool_errors_middleware(
    request,
    handler,
):
    """Convert tool exceptions into ToolMessages the model can handle."""
    try:
        async with cl.Step(name=request.tool_call["name"], type="tool") as step:
            res = await handler(request)
            step.output = res
            return res
    except Exception as e:
        message = f"Tool error: Please check your input and try again. ({e!r})"
        return ToolMessage(
            content=message,
            tool_call_id=request.tool_call["id"],
        )
