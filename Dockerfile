FROM python:3.13-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    python3-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN useradd --create-home --shell /bin/bash app

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false

RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

COPY app/ ./app/

RUN mkdir -p /app/data && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]