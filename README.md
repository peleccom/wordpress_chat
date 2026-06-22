# Wordpress deployment Chatbot

Chatbot for Wordpress deployment


## Tech Stack

- **Python**: 3.13
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **Linting**: ruff
- **Type Checking**: ty
- **Testing**: pytest


## Prerequisites

- [uv](https://github.com/astral-sh/uv)
- Python 3.13
- Docker & Docker Compose (for running tests and the app)


## Quick Start

### 1. Set Up Your Development Environment

Install the environment and the pre-commit hooks with

```bash
make install
```

This will also generate your `uv.lock` file


### 2. Run the app

```bash
make run
```
Navigate to [http://localhost:8000`](http://localhost:8000) to see chat


## Development

### Code quality

```bash
make check
```

Runs lockfile validation, pre-commit (lint, format), and type checking.

```bash
make test
```


### LangSmith monitoring (optional)

[LangSmith](https://smith.langchain.com/) provides traces and monitoring for LangChain-based LLM calls. To enable it locally or in deployment:

1. Sign in at [LangSmith](https://smith.langchain.com/) and open **Settings → API Keys → Create API Key**
2. Copy `.env.example` into `.env` and set:

```env
LANGSMITH_API_KEY=ls-your-api-key
LANGSMITH_TRACING=true
```
3. Run app and see traces in LangSmith


## Troubleshooting

### Run the pre-commit hooks

The CI/CD pipeline might be failing due to formatting issues. To resolve those run:

```bash
uv run pre-commit run -a
```

## Contributing

1. Install: `make install`
2. Before changes: `make check` and `make test`
3. After changes: `make check` and `make test`
4. Add tests for new features
5. Update docstrings when behavior changes
