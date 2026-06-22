"""Application settings for WordPress Insights Chat."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    app_name: str = "WordPress Insights Chat"
    debug: bool = False
    mcp_server_port: int = 8001
    api_port: int = 8000
    llm_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    llm_api_base: str = Field(default="", alias="OPENAI_BASE_URL")

    model_config = {"populate_by_name": True}


settings = AppSettings()
