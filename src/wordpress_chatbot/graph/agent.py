"""LangChain agent for WordPress insights using create_agent + LLM."""

from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from wordpress_chatbot.providers.wordpress_mock import WordPressMockProvider
from wordpress_chatbot.settings import settings

provider = WordPressMockProvider()


@tool
def get_site_info() -> dict[str, Any]:
    """Get basic WordPress site information (version, theme, plugins count)."""
    return provider.get_site_info()


@tool
def get_performance_metrics() -> dict[str, Any]:
    """Get site performance metrics (avg/p95 response times, error rate) and slowest pages."""
    return provider.get_performance_metrics()


@tool
def get_plugin_data() -> dict[str, Any]:
    """Get list of all plugins with active status and version, plus performance usage metrics per plugin."""
    return provider.get_plugin_data()


@tool
def get_security_report() -> dict[str, Any]:
    """Get security vulnerability summary and detailed findings with recommendations."""
    return provider.get_security_report()


@tool
def get_traffic_data() -> dict[str, Any]:
    """Get traffic summary with channel breakdown (organic, direct, social, referral)."""
    return provider.get_traffic_data()


@tool
def get_content_data() -> dict[str, Any]:
    """Get top-performing and underperforming (dead) content."""
    return provider.get_content_data()


@tool
def get_user_data() -> dict[str, Any]:
    """Get user statistics and list of inactive users."""
    return provider.get_user_data()


@tool
def get_recent_errors() -> list[dict[str, Any]]:
    """Get recent error log entries with timestamps, severity, and occurrence counts."""
    return provider.get_recent_errors()


tools = [
    get_site_info,
    get_performance_metrics,
    get_plugin_data,
    get_security_report,
    get_traffic_data,
    get_content_data,
    get_user_data,
    get_recent_errors,
]

SYSTEM_PROMPT = """You are a WordPress insights analysis assistant.

You have access to real WordPress site data through tools. Always use tools to gather data before answering.

Structure your responses with:
1. **Observation** — what the data shows
2. **Analysis** — why it matters
3. **Recommendation** — what to do about it

Use markdown formatting. Reference actual numbers from the data.
Keep responses concise — 2-3 paragraphs max."""

_agent = None


def get_agent():
    """Lazy-initialize and return the agent singleton."""
    global _agent
    if _agent is None:
        model_kwargs = {"model": settings.llm_model}
        if settings.llm_api_key:
            model_kwargs["api_key"] = settings.llm_api_key
        if settings.llm_api_base:
            model_kwargs["base_url"] = settings.llm_api_base
        model = ChatOpenAI(**model_kwargs)
        _agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
        )
    return _agent


def run_agent(question: str) -> dict[str, Any]:
    """Run the agent with a question and return the response."""
    agent = get_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    messages = result["messages"]
    response = messages[-1].content if messages else ""
    return {"response": response}
