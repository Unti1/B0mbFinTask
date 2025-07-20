FROM python:3.11-slim

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.1.2 \
    PATH="$POETRY_HOME/bin:$PATH" \
    POETRY_HOME=/usr/local/poetry

# Установка tini и других зависимостей
RUN apt-get update && \
    apt-get install -y curl build-essential tk libtk8.6 redis netcat-traditional tini && \
    apt-get clean

# Установка Poetry
RUN pip install poetry==$POETRY_VERSION

# Создание рабочей директории
WORKDIR /bomb_app

# Копируем файлы из нашего проекта в рабочую директорию
COPY pyproject.toml poetry.lock* /bomb_app/

RUN poetry --version

# Установка зависимостей (БЕЗ СОЗДАНИЯ ВИРТ. ОКР.)
RUN poetry config virtualenvs.create false && \
    poetry install --no-root

COPY . /bomb_app

# Используем tini как entrypoint
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["poetry", "run", "python", "main.py"]