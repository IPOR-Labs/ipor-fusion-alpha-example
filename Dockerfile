FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.21 /uv /uvx /bin/

WORKDIR /app

ENV UV_LINK_MODE=copy

# Install dependencies first so this layer is cached across code changes
COPY pyproject.toml uv.lock /app/
RUN uv sync --locked --no-dev

COPY . /app/

CMD ["/app/.venv/bin/python", "main.py"]
