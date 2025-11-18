# Dockerfile для универсального деплоя
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем uv для управления зависимостями
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Копируем файлы проекта
COPY pyproject.toml uv.lock ./
COPY src ./src

# Устанавливаем зависимости
RUN uv sync --frozen

# Запускаем бота
CMD ["uv", "run", "python", "src/bot.py"]

