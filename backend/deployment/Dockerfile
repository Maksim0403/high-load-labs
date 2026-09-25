FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --no-install-project --no-dev --locked

FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini ./

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
