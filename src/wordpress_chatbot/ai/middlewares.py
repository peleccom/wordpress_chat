import logging

from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage

from es_website_chatbot.ai.utils import handle_tool_errors

logger = logging.getLogger(__name__)


@wrap_tool_call  # ty: ignore[no-matching-overload]
async def handle_tool_errors_middleware(
    request,
    handler,
):
    """Convert tool exceptions into ToolMessages the model can handle."""
    logger.info("Calling tool `%s`", request.tool_call["name"])
    try:
        res = await handler(request)
        logger.info("Tool `%s` returned %s", request.tool_call["name"], res)
        return res
    except Exception as e:
        message = handle_tool_errors(e)
        return ToolMessage(
            content=message,
            tool_call_id=request.tool_call["id"],
        )
