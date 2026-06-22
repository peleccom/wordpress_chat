import chainlit as cl


async def show_tool_status_message(label: str):
    message = cl.Message(content="")
    await message.stream_token(label)
    return message


async def remove_meessage(m: cl.Message | None):
    if m:
        await m.remove()
