# Agent Guidance

## Developer Commands

```bash
make install   # Set up venv + install pre-commit hooks
make check     # Run lockfile check, pre-commit (lint+format), and ty type check
make run       # Run app via Docker Compose (http://localhost:8000)
make test      # Run pytest via Docker Compose (NOT direct pytest)
```

## Key Conventions

- **Tests run in Docker**: Always use `make test` or `make test-cov` — do not run `pytest` directly.
- **Pre-commit fix**: Run `uv run pre-commit run -a` to auto-fix lint issues before committing.
- **Type check**: Run `uv run ty check` (part of `make check`).
- **Lockfile validation**: `uv lock --locked` runs as part of `make check`.

## Architecture

- **App entrypoint**: `src/wordpress_chatbot/chat.py` (Chainlit app)
- **Main module**: `src/wordpress_chatbot/agent.py` (response logic)
- **Config**: `.chainlit/config.toml` for Chainlit settings
