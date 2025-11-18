"""Тесты для клиента GigaChat"""
from unittest.mock import Mock, patch, MagicMock
from src.gigachat_client import GigaChatClient


def test_check_parking_message_with_keywords():
    """Тест распознавания сообщения по ключевым словам"""
    client = GigaChatClient()
    is_parking, place_num = client.check_parking_message("Место 5 свободно")
    assert is_parking == True
    assert place_num == 5


def test_check_parking_message_variations():
    """Тест различных вариантов сообщений о парковке"""
    client = GigaChatClient()
    
    # Различные варианты формулировок
    test_cases = [
        ("Парковочное место 10 освободилось", 10),
        ("место 3 свободно", 3),
        ("Место номер 7 освободилось", 7),
    ]
    
    for message, expected_place in test_cases:
        is_parking, place_num = client.check_parking_message(message)
        assert is_parking == True, f"Не распознано: {message}"
        assert place_num == expected_place, f"Неправильный номер места для: {message}"


def test_check_parking_message_no_numbers():
    """Тест сообщения без чисел"""
    client = GigaChatClient()
    is_parking, place_num = client.check_parking_message("Привет, как дела?")
    assert is_parking == False
    assert place_num is None


def test_check_parking_message_no_keywords():
    """Тест сообщения с числами, но без ключевых слов о парковке"""
    client = GigaChatClient()
    is_parking, place_num = client.check_parking_message("Сегодня 15 градусов")
    assert is_parking == False
    assert place_num is None


def test_check_parking_message_negative():
    """Тест сообщения с отрицательными формулировками"""
    client = GigaChatClient()
    
    # Различные варианты отрицательных формулировок
    test_cases = [
        "Место 13 сегодня не свободно",
        "Место 5 занято",
        "Парковочное место 10 не освободилось",
        "Место 7 занято сегодня",
    ]
    
    for message in test_cases:
        is_parking, place_num = client.check_parking_message(message)
        assert is_parking == False, f"Не должно распознавать: {message}"
        assert place_num is None


def test_check_parking_message_with_gigachat():
    """Тест распознавания через GigaChat API (с моком)"""
    client = GigaChatClient()
    
    # Мокаем ответ GigaChat API
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "да"
    
    with patch.object(client.client, 'chat', return_value=mock_response):
        is_parking, place_num = client.check_parking_message("Освободилось парковочное место номер 12")
        assert is_parking == True
        assert place_num == 12


def test_check_parking_message_gigachat_negative():
    """Тест отрицательного ответа от GigaChat API"""
    client = GigaChatClient()
    
    # Мокаем отрицательный ответ GigaChat API
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "нет"
    
    with patch.object(client.client, 'chat', return_value=mock_response):
        is_parking, place_num = client.check_parking_message("Сегодня хорошая погода, 20 градусов")
        assert is_parking == False
        assert place_num is None


def test_check_parking_message_gigachat_error():
    """Тест обработки ошибки GigaChat API"""
    client = GigaChatClient()
    
    # Мокаем ошибку API
    # Используем сообщение без ключевых слов о парковке, но с числом, чтобы дошел до вызова GigaChat
    with patch.object(client.client, 'chat', side_effect=Exception("API Error")):
        is_parking, place_num = client.check_parking_message("Сегодня температура 5 градусов")
        # При ошибке должно вернуться False
        assert is_parking == False
        assert place_num is None

