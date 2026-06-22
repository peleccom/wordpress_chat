"""Chainlit chat UI handlers."""

from __future__ import annotations

import logging

import chainlit as cl

from wordpress_chatbot.graph.agent import run_agent

logger = logging.getLogger(__name__)


@cl.on_chat_start
async def on_chat_start() -> None:
    welcome = cl.Message(
        content="""# 🚀 WordPress Insights Chat

Welcome! Ask me anything about your WordPress site. I can analyze:

- **Performance** — speed, bottlenecks, slow pages
- **Security** — vulnerabilities, outdated plugins
- **Traffic** — visitor trends, channel breakdown
- **Content** — top posts, dead content
- **Plugins** — usage, impact, cleanup
- **Users** — engagement, inactive accounts

Try: *"Why is my site slow?"*, *"Which plugins should I remove?"*, *"What security issues exist?"*
""",
    )
    await welcome.send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    question = message.content.strip()
    if not question:
        return

    msg = cl.Message(content="")
    await msg.send()

    try:
        result = run_agent(question)
        await cl.Message(content=result["response"]).send()
    except Exception as exc:
        logger.exception("Error processing message")
        await cl.Message(content=f"⚠️ Sorry, something went wrong: {exc}").send()
