# Architecture

## Overview

```text
┌──────────────────────────────────┐
│     Single Server (port 8000)    │
│                                  │
│  ┌────────────┐  ┌────────────┐  │
│  │  Chainlit   │  │   FastMCP  │  │
│  │  Chat UI    │  │  SSE at    │  │
│  │  (/)        │  │  (/mcp)    │  │
│  └──────┬─────┘  └──────┬─────┘  │
└─────────┼────────────────┼────────┘
          │                │
          ▼                ▼
┌──────────────────────────────────┐
│   create_agent (LangChain)       │
│   LLM + 8 tools                  │
│   Observation → Analysis → Rec   │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│      WordPressMockProvider       │
│      (single data source)        │
└──────────────────────────────────┘
```

## Project Structure

```text
src/
└── wordpress_chatbot/
    ├── __init__.py
    ├── main.py             # FastAPI server (entry point)
    ├── chat.py             # Chainlit UI handlers
    ├── settings.py         # App configuration
    ├── graph/
    │   ├── agent.py        # create_agent + 8 LangChain tools
    │   └── middlewares.py  # Tool call middlewares
    ├── mcp/
    │   └── server.py       # FastMCP server (tools, resources, prompts)
    └── providers/
        └── wordpress_mock.py  # Mock WordPress data provider

tests/
└── test_providers.py        # Provider tests
```
