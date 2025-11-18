# Dockerfile для деплоя на Railway
FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt первым (для кеширования слоя)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY src ./src

# Запускаем бота
CMD ["python", "src/bot.py"]

