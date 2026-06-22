# WordPress Insights Chat — Agent Guide

## Quick Start

```bash
make install   # venv + pre-commit hooks
make run       # Docker Compose (http://localhost:8000), NO auto-rebuild
make test      # pytest in Docker — NOT direct `pytest`
make check     # uv lock --locked → pre-commit (ruff lint+format) → ty type check
```

Local dev (no Docker): `uv run python -m wordpress_chatbot` starts FastAPI on port 8000.
Requires `OPENAI_API_KEY` at runtime (not import time — lazy agent init).

## Key Commands

| Command | What it does |
|---------|-------------|
| `uv run pre-commit run -a` | Auto-fix lint issues |
| `uv run ty check` | Type check (part of `make check`) |

## Architecture

Single FastAPI server (port 8000) hosting **three things**:

- **Chainlit chat UI** at `/` — `src/wordpress_chatbot/chat.py` (handlers)
- **FastMCP SSE** at `/mcp` — `src/wordpress_chatbot/mcp/server.py`
- **LangChain agent** — `src/wordpress_chatbot/graph/agent.py` (`create_agent` + 8 tools)

Entry point: `src/wordpress_chatbot/main.py` — mounts MCP SSE, mounts Chainlit via `mount_chainlit`, adds `/mcp` → `/mcp/sse` redirect (307).

All data comes from `WordPressMockProvider` (`providers/wordpress_mock.py`) — single source for both LangChain tools and MCP tools.

Config via `settings.py` (pydantic-settings): `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`.

## Important Quirks

- **Tests run in Docker only** — `make test`. Direct `pytest` will fail due to missing Docker environment.
- **Pytest** skips AI tests by default (`addopts = "-m 'not ai'"`). `asyncio_mode = "auto"`.
- **`make run`** uses `docker compose run --rm` **without `--build`** — must manually rebuild after changes.
- **docker-compose** loads `./envs/local.env` (required) then `./.env` (optional, for secrets). Not `.env.example`.
