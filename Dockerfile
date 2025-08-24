FROM python:3.11-bookworm

WORKDIR /app

# Отключаем IPv6 для pip
RUN echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf && \
    echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf && \
    pip config set global.timeout 600 && \
    pip config set global.retries 5

COPY pyproject.toml poetry.lock ./

RUN pip install --timeout=600 --retries=5 --force-reinstall --prefer-binary poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY bot/ ./bot/

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

CMD ["python", "-m", "bot.main"]
