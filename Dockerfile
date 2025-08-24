FROM python:3.11-bookworm

WORKDIR /app

# Используйте зеркало Tsinghua University (Китай - быстрое)
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    pip config set global.timeout 600 && \
    pip config set global.retries 10

COPY pyproject.toml poetry.lock ./

RUN pip install --timeout=600 --retries=10 poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY bot/ ./bot/

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

CMD ["python", "-m", "bot.main"]
