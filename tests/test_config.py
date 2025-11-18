"""Тесты для модуля конфигурации"""
import os
from unittest.mock import patch
from src.config import (
    RAFFLE_TIMER_SECONDS,
    MAX_ACTIVE_RAFFLES,
    GIGACHAT_VERIFY_SSL,
    TELEGRAM_BOT_TOKEN,
    GIGACHAT_CLIENT_ID,
    GIGACHAT_CLIENT_SECRET,
)


def test_raffle_timer_default():
    """Проверка дефолтного значения таймера розыгрыша"""
    # Дефолтное значение должно быть 120 секунд (2 минуты)
    assert RAFFLE_TIMER_SECONDS == 120


def test_max_raffles_default():
    """Проверка дефолтного значения лимита активных розыгрышей"""
    # Дефолтное значение должно быть 5
    assert MAX_ACTIVE_RAFFLES == 5


def test_gigachat_verify_ssl_default():
    """Проверка дефолтного значения для SSL верификации"""
    # Дефолтное значение должно быть False
    assert GIGACHAT_VERIFY_SSL == False


def test_config_values_loaded():
    """Проверка, что значения конфигурации загружены (не None для обязательных)"""
    # Проверяем, что обязательные значения загружены из .env
    # (в реальном окружении они должны быть установлены)
    assert TELEGRAM_BOT_TOKEN is not None or os.getenv("TELEGRAM_BOT_TOKEN") is None
    assert GIGACHAT_CLIENT_ID is not None or os.getenv("GIGACHAT_CLIENT_ID") is None
    assert GIGACHAT_CLIENT_SECRET is not None or os.getenv("GIGACHAT_CLIENT_SECRET") is None

