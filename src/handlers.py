import threading
import random
import time
import logging
from telebot import types
from src.gigachat_client import GigaChatClient
from src.config import RAFFLE_TIMER_SECONDS, MAX_ACTIVE_RAFFLES

logger = logging.getLogger(__name__)

gigachat_client = GigaChatClient()

# Словарь активных розыгрышей: {raffle_id: {place_number, participants, message_id, chat_id, timer}}
active_raffles = {}

def handle_text_message(bot, message):
    """Обработчик текстовых сообщений"""
    # Проверка доступа уже выполнена в bot.py, здесь просто логируем
    chat_type = message.chat.type
    chat_title = message.chat.title if hasattr(message.chat, 'title') else 'личные сообщения'
    logger.info(f"Получено сообщение в {chat_type} '{chat_title}': {message.text}")
    
    # Проверяем через GigaChat, является ли это сообщение о свободном месте
    is_parking, place_number = gigachat_client.check_parking_message(message.text)
    
    if is_parking and place_number:
        # Проверяем лимит активных розыгрышей
        if len(active_raffles) >= MAX_ACTIVE_RAFFLES:
            # Удаляем самый старый розыгрыш
            remove_oldest_raffle(bot)
        
        # Создаем inline-кнопку "я хочу!"
        keyboard = types.InlineKeyboardMarkup()
        # Используем message_id как raffle_id для уникальности
        raffle_id = f"{message.chat.id}_{message.message_id}"
        button = types.InlineKeyboardButton(text="я хочу!", callback_data=f"want_{raffle_id}")
        keyboard.add(button)
        
        # Отправляем сообщение с кнопкой
        bot_message = bot.reply_to(message, "Место свободно! Кто хочет?", reply_markup=keyboard)
        
        # Сохраняем розыгрыш в словарь
        active_raffles[raffle_id] = {
            'place_number': place_number,
            'participants': [],
            'message_id': bot_message.message_id,
            'chat_id': message.chat.id,
            'timer': None,
            'timestamp': time.time()
        }
        
        # Запускаем таймер для розыгрыша
        timer = threading.Timer(RAFFLE_TIMER_SECONDS, finish_raffle, args=(bot, raffle_id))
        timer.start()
        active_raffles[raffle_id]['timer'] = timer
        
        logger.info(f"Обнаружено сообщение о свободном месте №{place_number}")

def handle_callback(bot, call):
    """Обработчик callback'ов кнопок"""
    if call.data.startswith("want_"):
        raffle_id = call.data.split("_", 1)[1]
        
        # Проверяем, существует ли розыгрыш
        if raffle_id not in active_raffles:
            bot.answer_callback_query(call.id, "Розыгрыш уже завершен")
            return
        
        # Получаем user_id
        user_id = call.from_user.id
        username = call.from_user.username or call.from_user.first_name
        
        # Проверяем, не участвовал ли уже пользователь
        raffle = active_raffles[raffle_id]
        if user_id in raffle['participants']:
            bot.answer_callback_query(call.id, "Вы уже участвуете!")
            return
        
        # Добавляем участника
        raffle['participants'].append(user_id)
        logger.info(f"Пользователь @{username} нажал кнопку для места №{raffle['place_number']}")
        
        # Подтверждаем нажатие
        bot.answer_callback_query(call.id, "Вы участвуете в розыгрыше!")

def remove_oldest_raffle(bot):
    """Удаляет самый старый розыгрыш при достижении лимита"""
    if not active_raffles:
        return
    
    # Находим самый старый розыгрыш по timestamp
    oldest_raffle_id = min(active_raffles.items(), key=lambda x: x[1]['timestamp'])[0]
    oldest_raffle = active_raffles[oldest_raffle_id]
    
    # Отменяем таймер, если он активен
    if oldest_raffle['timer']:
        oldest_raffle['timer'].cancel()
    
    logger.info(f"Удален самый старый розыгрыш места №{oldest_raffle['place_number']} из-за лимита активных розыгрышей")
    
    # Удаляем из словаря
    del active_raffles[oldest_raffle_id]

def finish_raffle(bot, raffle_id):
    """Завершает розыгрыш и выбирает победителя"""
    # Проверяем, существует ли еще розыгрыш
    if raffle_id not in active_raffles:
        return
    
    raffle = active_raffles[raffle_id]
    place_number = raffle['place_number']
    
    if raffle['participants']:
        # Случайный выбор победителя
        winner_id = random.choice(raffle['participants'])
        
        # Получаем информацию о победителе
        try:
            chat_member = bot.get_chat_member(raffle['chat_id'], winner_id)
            username = chat_member.user.username or chat_member.user.first_name
        except:
            username = "пользователь"
        
        # Отправляем сообщение с упоминанием победителя
        message_text = f"@{username}, место {place_number} теперь за тобой!"
        bot.send_message(raffle['chat_id'], message_text)
        
        logger.info(f"Победитель розыгрыша места №{place_number}: @{username}")
    else:
        # Никто не участвовал - очищаем розыгрыш
        logger.info(f"Розыгрыш места №{place_number} завершен, участников не было")
    
    # Удаляем розыгрыш из словаря
    del active_raffles[raffle_id]

