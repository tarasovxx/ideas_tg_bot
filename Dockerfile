FROM python:3.11-slim

# Настройка зеркал и таймаутов
RUN echo "deb http://mirror.yandex.ru/debian/ trixie main" > /etc/apt/sources.list && \
    echo "deb http://mirror.yandex.ru/debian/ trixie-updates main" >> /etc/apt/sources.list && \
    echo 'Acquire::http::Timeout "300";' > /etc/apt/apt.conf.d/99timeout && \
    echo 'Acquire::Retries "3";' >> /etc/apt/apt.conf.d/99timeout

# Установка пакетов с повторными попытками
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app
#
#RUN apt-get update && apt-get install -y \
#    gcc \
#    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root

COPY bot/ ./bot/

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

CMD ["python", "-m", "bot.main"]
