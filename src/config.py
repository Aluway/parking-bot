from dotenv import load_dotenv
import os
from pathlib import Path

# Загружаем .env из корня проекта
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Таймер розыгрыша (в секундах, по умолчанию 2 минуты = 120 секунд)
RAFFLE_TIMER_SECONDS = int(os.getenv("RAFFLE_TIMER_SECONDS", "120"))

# Лимит активных розыгрышей (по умолчанию 5)
MAX_ACTIVE_RAFFLES = int(os.getenv("MAX_ACTIVE_RAFFLES", "5"))

# GigaChat API
GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
GIGACHAT_VERIFY_SSL = os.getenv("GIGACHAT_VERIFY_SSL", "false").lower() == "true"

