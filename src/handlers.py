import threading
import random
import time
import logging
from datetime import date
from telebot import types
from src.gigachat_client import GigaChatClient
from src.config import RAFFLE_TIMER_SECONDS, MAX_ACTIVE_RAFFLES

logger = logging.getLogger(__name__)

gigachat_client = GigaChatClient()

# Словарь активных розыгрышей: {raffle_id: {place_number, participants, message_id, chat_id, timer, update_timer, start_time, date, winner_id}}
active_raffles = {}
# Множество победителей активных розыгрышей (для быстрой проверки)
active_winners = set()

def handle_text_message(bot, message):
    """Обработчик текстовых сообщений"""
    # Проверка доступа уже выполнена в bot.py, здесь просто логируем
    chat_type = message.chat.type
    chat_title = message.chat.title if hasattr(message.chat, 'title') else 'личные сообщения'
    logger.info(f"Получено сообщение в {chat_type} '{chat_title}': {message.text}")
    
    # Проверяем через GigaChat, является ли это сообщение о свободном месте
    is_parking, place_number = gigachat_client.check_parking_message(message.text)
    
    if is_parking and place_number:
        # Очищаем розыгрыши не сегодняшнего дня
        cleanup_old_raffles(bot)
        
        # Проверяем лимит активных розыгрышей
        if len(active_raffles) >= MAX_ACTIVE_RAFFLES:
            # Удаляем самый старый розыгрыш
            remove_oldest_raffle(bot)
        
        # Используем message_id как raffle_id для уникальности
        raffle_id = f"{message.chat.id}_{message.message_id}"
        start_time = time.time()
        raffle_date = date.today()
        
        # Создаем начальное сообщение с таймером
        message_text = format_raffle_message(place_number, RAFFLE_TIMER_SECONDS, 0)
        keyboard = create_raffle_keyboard(raffle_id, 0)
        
        # Отправляем сообщение с кнопкой
        bot_message = bot.reply_to(message, message_text, reply_markup=keyboard)
        
        # Сохраняем розыгрыш в словарь
        active_raffles[raffle_id] = {
            'place_number': place_number,
            'participants': [],
            'message_id': bot_message.message_id,
            'chat_id': message.chat.id,
            'timer': None,
            'update_timer': None,
            'timestamp': start_time,
            'start_time': start_time,
            'date': raffle_date,
            'winner_id': None
        }
        
        # Запускаем таймер для завершения розыгрыша
        timer = threading.Timer(RAFFLE_TIMER_SECONDS, finish_raffle, args=(bot, raffle_id))
        timer.start()
        active_raffles[raffle_id]['timer'] = timer
        
        # Запускаем периодическое обновление сообщения (каждые 10 секунд)
        update_timer = threading.Timer(10, update_raffle_message, args=(bot, raffle_id))
        update_timer.start()
        active_raffles[raffle_id]['update_timer'] = update_timer
        
        logger.info(f"Обнаружено сообщение о свободном месте №{place_number}")

def handle_callback(bot, call):
    """Обработчик callback'ов кнопок"""
    if call.data.startswith("want_"):
        raffle_id = call.data.split("_", 1)[1]
        
        # Проверяем, существует ли розыгрыш
        if raffle_id not in active_raffles:
            bot.answer_callback_query(call.id, "❌ Розыгрыш уже завершен", show_alert=True)
            return
        
        # Получаем user_id
        user_id = call.from_user.id
        username = call.from_user.username or call.from_user.first_name
        
        # Проверяем, не участвовал ли уже пользователь
        raffle = active_raffles[raffle_id]
        if user_id in raffle['participants']:
            bot.answer_callback_query(call.id, "⚠️ Вы уже участвуете!", show_alert=True)
            return
        
        # Проверяем, не является ли пользователь победителем одного из активных розыгрышей
        if user_id in active_winners:
            bot.answer_callback_query(
                call.id, 
                "🚫 Вы уже выиграли в одном из активных розыгрышей! Не можете участвовать в других.", 
                show_alert=True
            )
            return
        
        # Добавляем участника
        raffle['participants'].append(user_id)
        participants_count = len(raffle['participants'])
        logger.info(f"Пользователь @{username} нажал кнопку для места №{raffle['place_number']}")
        
        # Обновляем кнопку с новым количеством участников
        update_raffle_button(bot, raffle_id, raffle)
        
        # Подтверждаем нажатие
        bot.answer_callback_query(call.id, "✅ Вы участвуете в розыгрыше!")

def remove_oldest_raffle(bot):
    """Удаляет самый старый розыгрыш при достижении лимита"""
    if not active_raffles:
        return
    
    # Находим самый старый розыгрыш по timestamp
    oldest_raffle_id = min(active_raffles.items(), key=lambda x: x[1]['timestamp'])[0]
    oldest_raffle = active_raffles[oldest_raffle_id]
    
    # Удаляем победителя из списка активных победителей, если был
    if oldest_raffle.get('winner_id'):
        active_winners.discard(oldest_raffle['winner_id'])
    
    # Отменяем таймеры, если они активны
    if oldest_raffle['timer']:
        oldest_raffle['timer'].cancel()
    if oldest_raffle.get('update_timer'):
        oldest_raffle['update_timer'].cancel()
    
    logger.info(f"Удален самый старый розыгрыш места №{oldest_raffle['place_number']} из-за лимита активных розыгрышей")
    
    # Удаляем из словаря
    del active_raffles[oldest_raffle_id]


def cleanup_old_raffles(bot):
    """Удаляет розыгрыши, созданные не сегодня"""
    today = date.today()
    raffles_to_remove = []
    
    for raffle_id, raffle in active_raffles.items():
        if raffle.get('date') != today:
            raffles_to_remove.append(raffle_id)
    
    for raffle_id in raffles_to_remove:
        raffle = active_raffles[raffle_id]
        
        # Удаляем победителя из списка активных победителей, если был
        if raffle.get('winner_id'):
            active_winners.discard(raffle['winner_id'])
        
        # Отменяем таймеры
        if raffle['timer']:
            raffle['timer'].cancel()
        if raffle.get('update_timer'):
            raffle['update_timer'].cancel()
        
        logger.info(f"Удален розыгрыш места №{raffle['place_number']} (создан {raffle.get('date')}, сегодня {today})")
        del active_raffles[raffle_id]

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
        
        # Сохраняем победителя в розыгрыше
        raffle['winner_id'] = winner_id
        
        # Добавляем победителя в список активных победителей
        active_winners.add(winner_id)
        
        # Получаем информацию о победителе
        try:
            chat_member = bot.get_chat_member(raffle['chat_id'], winner_id)
            username = chat_member.user.username or chat_member.user.first_name
        except:
            username = "пользователь"
        
        # Отправляем сообщение с упоминанием победителя
        message_text = f"🎉 Поздравляем! 🎉\n\n🏆 Победитель розыгрыша места №{place_number}:\n@{username}\n\n🚗 Место теперь за тобой!"
        bot.send_message(raffle['chat_id'], message_text)
        
        logger.info(f"Победитель розыгрыша места №{place_number}: @{username} (ID: {winner_id})")
    else:
        # Никто не участвовал - очищаем розыгрыш
        logger.info(f"Розыгрыш места №{place_number} завершен, участников не было")
    
    # Отменяем таймер обновления, если он активен
    if raffle.get('update_timer'):
        raffle['update_timer'].cancel()
    
    # НЕ удаляем розыгрыш из словаря сразу - он останется в памяти до конца дня
    # Победитель будет удален из active_winners при cleanup_old_raffles или remove_oldest_raffle


def format_time_remaining(seconds: int) -> str:
    """Форматирует оставшееся время в читаемый вид"""
    if seconds <= 0:
        return "0с"
    
    minutes = seconds // 60
    secs = seconds % 60
    
    if minutes > 0:
        return f"{minutes}м {secs}с"
    else:
        return f"{secs}с"


def format_raffle_message(place_number: int, total_seconds: int, participants_count: int) -> str:
    """Форматирует сообщение розыгрыша с таймером"""
    time_str = format_time_remaining(total_seconds)
    return f"🎰 Розыгрыш места №{place_number}\n⏱ Осталось: {time_str}\n👥 Участников: {participants_count}\n\n🎯 Нажми кнопку, чтобы участвовать!"


def create_raffle_keyboard(raffle_id: str, participants_count: int) -> types.InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой и количеством участников"""
    keyboard = types.InlineKeyboardMarkup()
    if participants_count > 0:
        button_text = f"🙋 Я хочу! ({participants_count})"
    else:
        button_text = "🙋 Я хочу!"
    button = types.InlineKeyboardButton(text=button_text, callback_data=f"want_{raffle_id}")
    keyboard.add(button)
    return keyboard


def update_raffle_message(bot, raffle_id: str):
    """Обновляет сообщение розыгрыша с актуальным таймером и количеством участников"""
    if raffle_id not in active_raffles:
        return
    
    raffle = active_raffles[raffle_id]
    elapsed = time.time() - raffle['start_time']
    remaining = max(0, int(RAFFLE_TIMER_SECONDS - elapsed))
    participants_count = len(raffle['participants'])
    
    # Форматируем новое сообщение
    message_text = format_raffle_message(raffle['place_number'], remaining, participants_count)
    keyboard = create_raffle_keyboard(raffle_id, participants_count)
    
    try:
        # Обновляем сообщение
        bot.edit_message_text(
            message_text,
            chat_id=raffle['chat_id'],
            message_id=raffle['message_id'],
            reply_markup=keyboard
        )
    except Exception as e:
        # Игнорируем ошибки обновления (сообщение могло быть удалено)
        logger.debug(f"Не удалось обновить сообщение розыгрыша {raffle_id}: {e}")
    
    # Если время еще не истекло, планируем следующее обновление
    if remaining > 0:
        update_timer = threading.Timer(10, update_raffle_message, args=(bot, raffle_id))
        update_timer.start()
        raffle['update_timer'] = update_timer


def update_raffle_button(bot, raffle_id: str, raffle: dict):
    """Обновляет только кнопку с количеством участников"""
    if raffle_id not in active_raffles:
        return
    
    participants_count = len(raffle['participants'])
    keyboard = create_raffle_keyboard(raffle_id, participants_count)
    
    try:
        bot.edit_message_reply_markup(
            chat_id=raffle['chat_id'],
            message_id=raffle['message_id'],
            reply_markup=keyboard
        )
    except Exception as e:
        logger.debug(f"Не удалось обновить кнопку розыгрыша {raffle_id}: {e}")

