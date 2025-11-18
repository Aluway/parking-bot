# Parking Bot

Телеграмм-бот для розыгрыша свободных парковочных мест в групповом чате.

## Установка

1. Установите зависимости:
```bash
make install
```

2. Скопируйте `.env.example` в `.env` и заполните переменные:
```bash
cp .env.example .env
```

3. Заполните в `.env`:
   - `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота
   - `GIGACHAT_CLIENT_ID` - Client ID для GigaChat API
   - `GIGACHAT_CLIENT_SECRET` - Client Secret для GigaChat API

## Запуск

```bash
make run
```

## Тестирование

```bash
make test
```

## Документация

- [Идея проекта](docs/idea.md)
- [Техническое видение](docs/vision.md)
- [Правила разработки](docs/conventions.md)
- [План разработки](docs/tasklist.md)
