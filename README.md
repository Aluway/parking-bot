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
   - `OWNER_USER_ID` - ваш Telegram User ID (получить у [@userinfobot](https://t.me/userinfobot))
   - `ALLOWED_CHAT_IDS` - список ID разрешенных чатов через запятую (получить у [@getidsbot](https://t.me/getidsbot))

## Запуск

```bash
make run
```

## Тестирование

```bash
make test
```

## Безопасность

Бот защищен от несанкционированного использования:
- Работает только в разрешенных чатах (whitelist)
- Блокирует личные сообщения
- Контролирует добавление в группы (только владелец может добавлять)

Подробнее: [Документация по безопасности](docs/security.md)

## Документация

- [Идея проекта](docs/idea.md)
- [Техническое видение](docs/vision.md)
- [Правила разработки](docs/conventions.md)
- [План разработки](docs/tasklist.md)
- [Безопасность](docs/security.md)
