import asyncio
import logging

import chainlit as cl
from wordpress_chatbot.ai.context import ChatContext
from wordpress_chatbot.ai.tool_status import status_for_tool_calls
from wordpress_chatbot.app import app
from wordpress_chatbot.core.chainlit_utls import (remove_meessage,
                                                   show_tool_status_message)
from fastapi.security.oauth2 import OAuth2Model, OAuthFlowsModel
from langchain.messages import AIMessage, HumanMessage
from langchain_core.messages import AIMessageChunk

# Fix openapi docs. See https://github.com/Chainlit/chainlit/issues/1906
cl.auth.reuseable_oauth.model = OAuth2Model(
    flows=OAuthFlowsModel(), description="OAuth2 with Authorization Code and Cookies"
)

logger = logging.getLogger(__name__)




@cl.on_message
async def on_message(message: cl.Message):
    await process_user_message(message.content)


async def _stream_message(thread_id: str, user: cl.User, content: str):
    config = {"configurable": {"thread_id": thread_id}}
    context = ChatContext(user_id=user.identifier)
    final_answer = cl.Message(content="")
    working_message: cl.Message | None = None
    # stream_mode="messages" captures the output from the final node
    async for msg, metadata in app.state.agent_graph.astream(
        {"messages": [HumanMessage(content=content)]},
        stream_mode="messages",
        config=config,
        context=context,
    ):
        if isinstance(msg, AIMessage):

            internal_node = metadata.get("disable_streaming") and isinstance(msg, AIMessageChunk)
            if msg.tool_calls:
                label = status_for_tool_calls(msg.tool_calls)
                if label:
                    if working_message is None:
                        working_message = await show_tool_status_message(label)
                    elif working_message.content != label:
                        await working_message.remove()
                        await asyncio.sleep(0.5)
                        working_message = await show_tool_status_message(label)
            elif not msg.tool_calls and not internal_node and msg.content:
                await remove_meessage(working_message)
                working_message = None
                await final_answer.stream_token(msg.content)
    await remove_meessage(working_message)
    await final_answer.send()


async def process_user_message(content: str) -> None:
    if not (user := cl.context.session.user):
        return


    thread_id = _chainlit_thread_id()
    cl.user_session.set("thread_id", thread_id)
    try:
        await _stream_message(thread_id, user, content)
    except Exception:
        logger.exception("Error while processing message")
        await cl.Message(content="Oops! Something went wrong while processing your message 🙈").send()

def _chainlit_thread_id() -> str:
    """Chainlit conversation thread id (threads.id / steps.threadId), not websocket session.id."""
    return cl.context.session.thread_id
