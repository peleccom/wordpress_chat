# WordPress Insights Chat

AI-powered WordPress analytics platform with MCP (Model Context Protocol), LangChain agent orchestration, and Chainlit chat UI.

Ask natural language questions about your WordPress deployment and receive actionable insights — all powered by mock data for development.

> See [`demo.md`](demo.md) for screenshots and usage examples.
> See [`architecture.md`](architecture.md) for project structure and architecture details.

## Quick Start

```bash
# 1. Install dependencies
make install

# 2. Start the app
make run
```

Open **http://localhost:8000** for the Chainlit streaming chat UI.

Use **http://localhost:8000/mcp** to connect an MCP client.

## Install

```bash
make install
```

## Tech Stack

- **Python** 3.13
- **Chainlit** — Chat UI (hosts the server)
- **FastMCP** — MCP server with tools, resources, and prompts (mounted on Chainlit)
- **LangChain** — `create_agent` with LLM-powered tool calling
- **Pydantic v2** — Configuration
- **pytest** — Testing

## Features

### 🔧 MCP Tools (8 tools)
Analyze every aspect of a WordPress site:

| Tool | Data |
|------|------|
| `get_site_info` | WordPress version, PHP, theme, plugin count |
| `get_performance_metrics` | Response times, error rate, slowest pages |
| `get_plugin_data` | Plugin list + per-plugin execution times |
| `get_security_report` | Vulnerability counts + detailed findings |
| `get_traffic_data` | Traffic volume, channel breakdown, bounce rate |
| `get_content_data` | Top-performing and dead content |
| `get_user_data` | User stats + inactive user list |
| `get_recent_errors` | Recent errors with severity and counts |

### 🧠 LLM-Powered Agent (`create_agent`)
Uses LangChain's `create_agent` with a ReAct loop — the LLM decides which tools to call and generates structured insights:

1. **Observation** — what the data shows
2. **Analysis** — why it matters
3. **Recommendation** — what to do about it


## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv)
- An LLM API key (e.g., `OPENAI_API_KEY` for `gpt-4o-mini`)

### Run Tests

```bash
make test
```

### Start the Server

```bash
# Set your API key
export OPENAI_API_KEY="sk-..."

# Start the server (FastAPI + Chainlit UI + MCP)
uv run python -m wordpress_chatbot
```

Then open **http://localhost:8000** to chat.

The MCP server is available at **http://localhost:8000/mcp** (redirects to SSE).

## Example Questions

| Category | Question |
|----------|----------|
| Performance | "Why is my site slow?" |
| Security | "Are there security risks?" |
| Traffic | "Why did traffic decrease?" |
| Content | "What content performs best?" |
| Plugins | "Which plugins impact performance?" |
| Users | "Which users are inactive?" |
| Mixed | "Give me a site overview" |

## Configuration

Set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | LLM API key (required) |
| `OPENAI_MODEL` | `gpt-4o-mini` | LLM model name |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Custom API base URL |

## Example Output

```
**Observation:** Average response time is 2300ms (above 2s threshold).
P95 is 3900ms — 5% of users experience slow loads.

**Analysis:** WooCommerce contributes 420ms avg execution time,
and /shop is the slowest page at 4100ms.

**Recommendations:**
1. Enable page caching (WP Rocket / WP Super Cache)
2. Investigate WooCommerce hooks on /shop
3. Implement a CDN for static assets
```

## Testing

```bash
make test      # Run tests in Docker
```

## Development

```bash
make install   # Set up venv + pre-commit
make check     # Lint + type check
```

## License

MIT
