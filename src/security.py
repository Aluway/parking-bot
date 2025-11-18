"""Модуль безопасности для проверки доступа"""
import logging
from src.config import OWNER_USER_ID, ALLOWED_CHAT_IDS

logger = logging.getLogger(__name__)


def is_allowed_chat(chat_id: int) -> bool:
    """
    Проверяет, разрешен ли чат для работы бота.
    
    Args:
        chat_id: ID чата для проверки
        
    Returns:
        True если чат разрешен, False иначе
    """
    is_allowed = chat_id in ALLOWED_CHAT_IDS
    if not is_allowed:
        logger.warning(f"Попытка доступа из неразрешенного чата: {chat_id}")
    return is_allowed


def is_private_message(chat_type: str) -> bool:
    """
    Проверяет, является ли сообщение личным.
    
    Args:
        chat_type: Тип чата (private, group, supergroup, channel)
        
    Returns:
        True если это личное сообщение, False иначе
    """
    return chat_type == "private"


def is_owner(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь владельцем бота.
    
    Args:
        user_id: ID пользователя для проверки
        
    Returns:
        True если пользователь является владельцем, False иначе
    """
    return user_id == OWNER_USER_ID


def check_chat_access(chat_id: int, chat_type: str) -> tuple[bool, str]:
    """
    Проверяет доступ к чату. Блокирует личные сообщения и неразрешенные чаты.
    
    Args:
        chat_id: ID чата
        chat_type: Тип чата
        
    Returns:
        tuple[bool, str]: (разрешен, причина отказа)
    """
    # Блокируем личные сообщения
    if is_private_message(chat_type):
        return False, "Бот не работает в личных сообщениях"
    
    # Проверяем разрешенные чаты
    if not is_allowed_chat(chat_id):
        return False, "Чат не разрешен для работы бота"
    
    return True, ""


def check_owner_permission(user_id: int) -> bool:
    """
    Проверяет, имеет ли пользователь права владельца.
    
    Args:
        user_id: ID пользователя
        
    Returns:
        True если пользователь является владельцем
    """
    if not is_owner(user_id):
        logger.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
        return False
    return True

