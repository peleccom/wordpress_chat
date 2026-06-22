# Install uv
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV PYTHONUNBUFFERED=1
# Change the working directory to the `app` directory
WORKDIR /app

# Copy the lockfile and `pyproject.toml` into the image
COPY pyproject.toml uv.lock /app/

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the project into the image
COPY . /app

# Sync the project. Install spacy models
RUN uv sync --frozen && uv run spacy download en_core_web_md

CMD ["/app/.venv/bin/fastapi", "run", "--app", "app", "src/wordpress_chatbot/app.py"]
