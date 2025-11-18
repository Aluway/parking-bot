import re
import logging
from gigachat import GigaChat
from src.config import GIGACHAT_CLIENT_SECRET, GIGACHAT_VERIFY_SSL

logger = logging.getLogger(__name__)


class GigaChatClient:
    def __init__(self):
        """Инициализация клиента GigaChat API"""
        # Используем authorization key (GIGACHAT_CLIENT_SECRET) как credentials
        self.client = GigaChat(
            credentials=GIGACHAT_CLIENT_SECRET,
            verify_ssl_certs=GIGACHAT_VERIFY_SSL
        )
        # Создаем паттерны один раз для переиспользования
        self.parking_pattern = re.compile(r'место|парков', re.IGNORECASE)
        self.free_pattern = re.compile(r'свобод|освобод', re.IGNORECASE)
    
    def check_parking_message(self, message_text: str) -> tuple[bool, int | None]:
        """
        Проверяет, является ли сообщение объявлением о свободном месте.
        
        Args:
            message_text: Текст сообщения для проверки
            
        Returns:
            tuple[bool, int | None]: (is_parking_message, place_number)
            - is_parking_message: True если сообщение о свободном месте
            - place_number: номер места или None
        """
        # Проверяем, является ли сообщение вопросом
        message_lower = message_text.lower().strip()
        
        # Проверка на вопросительный знак
        if '?' in message_text:
            logger.info("Обнаружен вопросительный знак, сообщение является вопросом")
            return False, None
        
        # Проверка на вопросительные слова и конструкции
        question_patterns = [
            r'\b(какое|какой|какая|какие)\b',
            r'\b(где|когда|кто|что|как|почему|зачем)\b',
            r'\b(свободно\s+ли|свободно\s+или|свободно\?|свободно\s+нет)\b',
            r'\b(освободилось\s+ли|освободилось\s+или)\b',
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                logger.info(f"Обнаружен вопрос по паттерну '{pattern}', сообщение является вопросом")
                return False, None
        
        # Извлекаем числа из сообщения
        numbers_in_message = re.findall(r'\d+', message_text)
        
        # Если нет чисел, сразу возвращаем False
        if not numbers_in_message:
            return False, None
        
        # Проверяем через байтовое сравнение (избегаем проблем с кодировкой)
        try:
            message_bytes = message_text.encode('utf-8')
        except (UnicodeEncodeError, AttributeError):
            # Если не удалось закодировать, пробуем как есть
            message_bytes = str(message_text).encode('utf-8', errors='replace')
        
        # Байтовые представления ключевых слов в UTF-8
        parking_bytes_list = [
            b'\xd0\xbc\xd0\xb5\xd1\x81\xd1\x82\xd0\xbe',  # место
            b'\xd0\x9c\xd0\xb5\xd1\x81\xd1\x82\xd0\xbe',  # Место
            b'\xd0\x9c\xd0\x95\xd0\xa1\xd0\xa2\xd0\x9e',  # МЕСТО
            b'\xd0\xbf\xd0\xb0\xd1\x80\xd0\xba\xd0\xbe\xd0\xb2',  # парков
        ]
        free_bytes_list = [
            b'\xd1\x81\xd0\xb2\xd0\xbe\xd0\xb1\xd0\xbe\xd0\xb4',  # свобод
            b'\xd0\xa1\xd0\xb2\xd0\xbe\xd0\xb1\xd0\xbe\xd0\xb4',  # Свобод
            b'\xd0\xa1\xd0\x92\xd0\x9e\xd0\x91\xd0\x9e\xd0\x94',  # СВОБОД
            b'\xd0\xbe\xd1\x81\xd0\xb2\xd0\xbe\xd0\xb1\xd0\xbe\xd0\xb4',  # освобод
        ]
        # Отрицательные формулировки (не свободно, занято и т.д.)
        negative_bytes_list = [
            b'\xd0\xbd\xd0\xb5 \xd1\x81\xd0\xb2\xd0\xbe\xd0\xb1\xd0\xbe\xd0\xb4',  # не свобод
            b'\xd0\x9d\xd0\xb5 \xd1\x81\xd0\xb2\xd0\xbe\xd0\xb1\xd0\xbe\xd0\xb4',  # Не свобод
            b'\xd0\xbd\xd0\xb5\xd1\x81\xd0\xb2\xd0\xbe\xd0\xb1\xd0\xbe\xd0\xb4',  # несвобод
            b'\xd0\xbd\xd0\xb5 \xd0\xbe\xd1\x81\xd0\xb2\xd0\xbe\xd0\xb1\xd0\xbe\xd0\xb4',  # не освобод
            b'\xd0\x9d\xd0\xb5 \xd0\xbe\xd1\x81\xd0\xb2\xd0\xbe\xd0\xb1\xd0\xbe\xd0\xb4',  # Не освобод
            b'\xd0\xb7\xd0\xb0\xd0\xbd\xd1\x8f\xd1\x82',  # занят
            b'\xd0\x97\xd0\xb0\xd0\xbd\xd1\x8f\xd1\x82',  # Занят
            b'\xd0\xb7\xd0\xb0\xd0\xbd\xd1\x8f\xd1\x82\xd0\xbe',  # занято
            b'\xd0\x97\xd0\xb0\xd0\xbd\xd1\x8f\xd1\x82\xd0\xbe',  # Занято
        ]
        
        # Сначала проверяем отрицательные формулировки (приоритет)
        has_negative = any(nb in message_bytes for nb in negative_bytes_list)
        if has_negative:
            logger.info("Обнаружена отрицательная формулировка, сообщение не о свободном месте")
            return False, None
        
        has_parking = any(pb in message_bytes for pb in parking_bytes_list)
        has_free = any(fb in message_bytes for fb in free_bytes_list)
        
        # Если есть ключевые слова о парковке и свободе, возвращаем результат
        if has_parking and has_free:
            place_num = int(numbers_in_message[0])
            logger.info(f"Обнаружено сообщение о свободном месте №{place_num}")
            return True, place_num
        
        # Для более сложных случаев используем GigaChat
        prompt = f"""Это сообщение о свободном парковочном месте? Ответь только "да" или "нет".

Сообщение: {message_text}"""
        
        try:
            response = self.client.chat(prompt)
            result_raw = response.choices[0].message.content
            
            # Проверяем кодировку и правильно декодируем
            if isinstance(result_raw, bytes):
                result = result_raw.decode('utf-8').strip().lower()
            else:
                result = str(result_raw).strip().lower()
            
            # Если GigaChat подтвердил, что это сообщение о свободном месте
            if "да" in result or "yes" in result:
                place_num = int(numbers_in_message[0])
                logger.info(f"Обнаружено сообщение о свободном месте №{place_num}")
                return True, place_num
            
            return False, None
        except Exception as e:
            logger.error(f"Ошибка GigaChat API: {e}")
            return False, None

