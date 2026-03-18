FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
# Создаем рабочую директорию
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src




# Устанавливаем Poetry
RUN pip install poetry==1.8.3

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости через Poetry в системный Python
RUN poetry config virtualenvs.create false && \
    poetry config virtualenvs.in-project false && \
    poetry install --no-root

COPY src/ ./src/

# Открываем порт
EXPOSE 8000

# Точка входа через Poetry
CMD ["poetry", "run", "python", "-m", "main"]

