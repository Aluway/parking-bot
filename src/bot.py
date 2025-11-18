import sys
import logging
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import telebot
from src.config import TELEGRAM_BOT_TOKEN
from src.handlers import handle_text_message, handle_callback

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(content_types=['text'])
def message_handler(message):
    """Обработчик всех текстовых сообщений"""
    # Команда для проверки статуса (временная, для тестирования)
    if message.text and message.text.startswith('/status'):
        from src.handlers import active_raffles
        if active_raffles:
            status_text = "Активные розыгрыши:\n"
            for raffle_id, raffle in active_raffles.items():
                status_text += f"  Место №{raffle['place_number']}: {len(raffle['participants'])} участников\n"
            bot.reply_to(message, status_text)
        else:
            bot.reply_to(message, "Нет активных розыгрышей")
        return
    
    # Проверяем, что это текст (не команда бота)
    if message.text and not message.text.startswith('/'):
        handle_text_message(bot, message)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Обработчик callback'ов от inline-кнопок"""
    handle_callback(bot, call)

if __name__ == "__main__":
    logger.info("Бот запущен и готов к работе")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")

