"""Тесты для обработчиков сообщений"""
import time
from unittest.mock import Mock, MagicMock, patch
from src.handlers import (
    finish_raffle,
    remove_oldest_raffle,
    active_raffles,
)


def setup_function():
    """Очистка активных розыгрышей перед каждым тестом"""
    active_raffles.clear()


def test_finish_raffle_with_winner():
    """Тест завершения розыгрыша с выбором победителя"""
    mock_bot = Mock()
    mock_bot.get_chat_member.return_value = MagicMock()
    mock_bot.get_chat_member.return_value.user = MagicMock()
    mock_bot.get_chat_member.return_value.user.username = "test_user"
    mock_bot.send_message = Mock()
    
    raffle_id = "test_raffle_1"
    active_raffles[raffle_id] = {
        'place_number': 5,
        'participants': [123, 456, 789],
        'message_id': 100,
        'chat_id': -100,
        'timer': None,
        'timestamp': time.time()
    }
    
    # Запускаем завершение розыгрыша
    finish_raffle(mock_bot, raffle_id)
    
    # Проверяем, что розыгрыш удален
    assert raffle_id not in active_raffles
    
    # Проверяем, что было отправлено сообщение
    assert mock_bot.send_message.called
    call_args = mock_bot.send_message.call_args
    assert call_args[0][0] == -100  # chat_id
    message_text = call_args[0][1]
    assert "место" in message_text.lower() or "№5" in message_text or "№ 5" in message_text
    assert "@test_user" in message_text


def test_finish_raffle_no_participants():
    """Тест завершения розыгрыша без участников"""
    mock_bot = Mock()
    
    raffle_id = "test_raffle_2"
    active_raffles[raffle_id] = {
        'place_number': 3,
        'participants': [],
        'message_id': 101,
        'chat_id': -100,
        'timer': None,
        'timestamp': time.time()
    }
    
    # Запускаем завершение розыгрыша
    finish_raffle(mock_bot, raffle_id)
    
    # Проверяем, что розыгрыш удален
    assert raffle_id not in active_raffles
    
    # Проверяем, что сообщение не отправлялось
    assert not mock_bot.send_message.called


def test_finish_raffle_nonexistent():
    """Тест завершения несуществующего розыгрыша"""
    mock_bot = Mock()
    
    raffle_id = "nonexistent_raffle"
    
    # Пытаемся завершить несуществующий розыгрыш
    finish_raffle(mock_bot, raffle_id)
    
    # Проверяем, что ничего не произошло
    assert not mock_bot.send_message.called


def test_remove_oldest_raffle():
    """Тест удаления самого старого розыгрыша"""
    mock_bot = Mock()
    
    # Создаем несколько розыгрышей с разными timestamp
    current_time = time.time()
    active_raffles["raffle_1"] = {
        'place_number': 1,
        'participants': [],
        'message_id': 1,
        'chat_id': -100,
        'timer': None,
        'timestamp': current_time - 100  # Самый старый
    }
    active_raffles["raffle_2"] = {
        'place_number': 2,
        'participants': [],
        'message_id': 2,
        'chat_id': -100,
        'timer': None,
        'timestamp': current_time - 50
    }
    active_raffles["raffle_3"] = {
        'place_number': 3,
        'participants': [],
        'message_id': 3,
        'chat_id': -100,
        'timer': None,
        'timestamp': current_time  # Самый новый
    }
    
    # Удаляем самый старый
    remove_oldest_raffle(mock_bot)
    
    # Проверяем, что самый старый удален
    assert "raffle_1" not in active_raffles
    assert "raffle_2" in active_raffles
    assert "raffle_3" in active_raffles


def test_remove_oldest_raffle_with_timer():
    """Тест удаления розыгрыша с активным таймером"""
    mock_bot = Mock()
    mock_timer = Mock()
    mock_timer.cancel = Mock()
    
    raffle_id = "raffle_with_timer"
    active_raffles[raffle_id] = {
        'place_number': 1,
        'participants': [],
        'message_id': 1,
        'chat_id': -100,
        'timer': mock_timer,
        'timestamp': time.time() - 100
    }
    
    # Удаляем розыгрыш
    remove_oldest_raffle(mock_bot)
    
    # Проверяем, что таймер был отменен
    assert mock_timer.cancel.called
    assert raffle_id not in active_raffles


def test_remove_oldest_raffle_empty():
    """Тест удаления при пустом словаре розыгрышей"""
    mock_bot = Mock()
    
    # Убеждаемся, что словарь пуст
    assert len(active_raffles) == 0
    
    # Пытаемся удалить (не должно быть ошибки)
    remove_oldest_raffle(mock_bot)
    
    # Словарь должен остаться пустым
    assert len(active_raffles) == 0

