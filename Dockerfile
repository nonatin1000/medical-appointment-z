# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.4.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./
# Inclui o grupo dev para ter langgraph-cli (Studio) na mesma imagem.
RUN poetry install --with dev --no-root --no-ansi

COPY app ./app
COPY langgraph.json ./

EXPOSE 8000 2024

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
