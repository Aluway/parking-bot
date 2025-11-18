import sys
import logging
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import telebot
from src.config import TELEGRAM_BOT_TOKEN
from src.handlers import handle_text_message, handle_callback
from src.security import check_chat_access, check_owner_permission, is_owner

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    """Обработчик добавления участников в группу"""
    # Проверяем, добавили ли бота
    bot_info = bot.get_me()
    new_members = message.new_chat_members
    
    for member in new_members:
        if member.id == bot_info.id:
            # Бота добавили в группу
            chat_id = message.chat.id
            added_by = message.from_user.id if message.from_user else None
            
            # Проверяем, разрешен ли чат
            from src.security import is_allowed_chat
            if is_allowed_chat(chat_id):
                # Чат разрешен - все в порядке
                logger.info(f"Бот добавлен в разрешенный чат {chat_id}")
            else:
                # Чат не разрешен, проверяем, добавил ли владелец
                if added_by and is_owner(added_by):
                    # Владелец добавил - разрешаем (но нужно добавить в ALLOWED_CHAT_IDS вручную)
                    logger.info(f"Владелец добавил бота в новый чат {chat_id}. Необходимо добавить чат в ALLOWED_CHAT_IDS")
                    bot.send_message(
                        chat_id,
                        "Бот добавлен владельцем. Для работы необходимо добавить ID чата в конфигурацию."
                    )
                else:
                    # Не владелец добавил - покидаем группу
                    logger.warning(f"Попытка добавления бота в неразрешенный чат {chat_id} пользователем {added_by}")
                    bot.send_message(
                        chat_id,
                        "Бот работает только в разрешенных чатах. Покидаю группу."
                    )
                    try:
                        bot.leave_chat(chat_id)
                    except Exception as e:
                        logger.error(f"Ошибка при попытке покинуть чат: {e}")
            break

@bot.message_handler(content_types=['text'])
def message_handler(message):
    """Обработчик всех текстовых сообщений"""
    # Проверка доступа к чату
    allowed, reason = check_chat_access(message.chat.id, message.chat.type)
    if not allowed:
        logger.warning(f"Доступ запрещен: {reason} (чат: {message.chat.id}, тип: {message.chat.type})")
        # В личных сообщениях можно ответить, в группах - просто игнорируем
        if message.chat.type == "private":
            bot.reply_to(message, "Бот не работает в личных сообщениях. Добавьте бота в группу.")
        return
    
    # Команда для проверки статуса (только для владельца)
    if message.text and message.text.startswith('/status'):
        if not check_owner_permission(message.from_user.id if message.from_user else 0):
            bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
            return
            
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
    # Проверка доступа к чату
    allowed, reason = check_chat_access(call.message.chat.id, call.message.chat.type)
    if not allowed:
        logger.warning(f"Доступ запрещен для callback: {reason} (чат: {call.message.chat.id})")
        bot.answer_callback_query(call.id, "Доступ запрещен", show_alert=True)
        return
    
    handle_callback(bot, call)

if __name__ == "__main__":
    logger.info("Бот запущен и готов к работе")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")

