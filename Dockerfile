# Install uv
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock /app/

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the project
COPY . /app

# Sync the project
RUN uv sync --frozen

# Default: run MCP server + Chainlit (override for different modes)
CMD ["uv", "run", "fastapi", "run", "src/wordpress_chatbot/main.py"]
