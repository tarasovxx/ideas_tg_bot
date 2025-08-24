FROM python:3.11-bookworm

WORKDIR /app

# Настройка российского зеркала PyPI
RUN pip config set global.index-url https://pypi.python.org/simple/ && \
    pip config set global.trusted-host pypi.python.org && \
    pip config set global.timeout 300

COPY pyproject.toml poetry.lock ./

RUN pip install --timeout=300 poetry && \
    poetry config virtualenvs.create false && \
    poetry config repositories.default https://pypi.python.org/simple/ && \
    poetry install --no-interaction --no-ansi --no-root

COPY bot/ ./bot/

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

CMD ["python", "-m", "bot.main"]
