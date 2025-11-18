"""Тесты для модуля безопасности"""
import os
from unittest.mock import patch
from src.security import (
    is_allowed_chat,
    is_private_message,
    is_owner,
    check_chat_access,
    check_owner_permission,
)
from src.config import OWNER_USER_ID, ALLOWED_CHAT_IDS


def test_is_private_message():
    """Тест проверки личных сообщений"""
    assert is_private_message("private") == True
    assert is_private_message("group") == False
    assert is_private_message("supergroup") == False
    assert is_private_message("channel") == False


def test_is_owner():
    """Тест проверки владельца"""
    # Тест зависит от конфигурации, но проверяем логику
    if OWNER_USER_ID > 0:
        assert is_owner(OWNER_USER_ID) == True
        assert is_owner(OWNER_USER_ID + 1) == False
    else:
        # Если OWNER_USER_ID не установлен, все должны быть False
        assert is_owner(123456) == False


def test_is_allowed_chat():
    """Тест проверки разрешенных чатов"""
    # Тест зависит от конфигурации
    if ALLOWED_CHAT_IDS:
        for chat_id in ALLOWED_CHAT_IDS:
            assert is_allowed_chat(chat_id) == True
    
    # Неразрешенный чат должен вернуть False
    assert is_allowed_chat(999999999) == False


def test_check_chat_access_private():
    """Тест блокировки личных сообщений"""
    allowed, reason = check_chat_access(123456, "private")
    assert allowed == False
    assert "личных сообщениях" in reason.lower() or "private" in reason.lower()


def test_check_chat_access_allowed():
    """Тест доступа к разрешенному чату"""
    # Если есть разрешенные чаты, проверяем один из них
    if ALLOWED_CHAT_IDS:
        chat_id = ALLOWED_CHAT_IDS[0]
        allowed, reason = check_chat_access(chat_id, "group")
        assert allowed == True
        assert reason == ""


def test_check_chat_access_not_allowed():
    """Тест блокировки неразрешенного чата"""
    allowed, reason = check_chat_access(999999999, "group")
    assert allowed == False
    assert "разрешен" in reason.lower() or "allowed" in reason.lower()


def test_check_owner_permission():
    """Тест проверки прав владельца"""
    if OWNER_USER_ID > 0:
        assert check_owner_permission(OWNER_USER_ID) == True
        assert check_owner_permission(OWNER_USER_ID + 1) == False
    else:
        # Если OWNER_USER_ID не установлен, все должны быть False
        assert check_owner_permission(123456) == False

