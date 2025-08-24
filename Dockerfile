FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root

COPY bot/ ./bot/

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

CMD ["python", "-m", "bot.main"]
