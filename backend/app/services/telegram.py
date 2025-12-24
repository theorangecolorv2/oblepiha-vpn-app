"""
Валидация Telegram Web App initData.
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import parse_qs, unquote

from app.config import get_settings
from app.schemas.user import UserFromTelegram

logger = logging.getLogger(__name__)


def validate_init_data(init_data: str, max_age_seconds: int = 86400) -> bool:
    """
    Валидация initData от Telegram Web App.
    
    Args:
        init_data: Строка initData от Telegram
        max_age_seconds: Максимальный возраст данных (по умолчанию 24 часа)
    
    Returns:
        True если данные валидны
    """
    settings = get_settings()
    bot_token = settings.telegram_bot_token
    
    try:
        # Парсим данные
        parsed = parse_qs(init_data)
        
        # Получаем hash
        received_hash = parsed.get("hash", [None])[0]
        if not received_hash:
            logger.warning("No hash in initData")
            return False
        
        # Проверяем auth_date (время создания данных)
        auth_date_str = parsed.get("auth_date", [None])[0]
        if auth_date_str:
            auth_date = datetime.fromtimestamp(int(auth_date_str))
            if datetime.now() - auth_date > timedelta(seconds=max_age_seconds):
                logger.warning(f"initData expired: {auth_date}")
                return False
        
        # Формируем строку для проверки (все параметры кроме hash, отсортированные)
        data_check_items = []
        for key, values in sorted(parsed.items()):
            if key != "hash":
                data_check_items.append(f"{key}={values[0]}")
        
        data_check_string = "\n".join(data_check_items)
        
        # Создаём secret_key = HMAC_SHA256(bot_token, "WebAppData")
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Сравниваем
        is_valid = hmac.compare_digest(calculated_hash, received_hash)
        
        if not is_valid:
            logger.warning("initData hash mismatch")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error validating initData: {e}")
        return False


def parse_user_from_init_data(init_data: str) -> Optional[UserFromTelegram]:
    """
    Извлечь данные пользователя из initData.
    
    Args:
        init_data: Строка initData от Telegram
    
    Returns:
        UserFromTelegram или None если не удалось распарсить
    """
    try:
        parsed = parse_qs(init_data)
        user_json = parsed.get("user", [None])[0]
        
        if not user_json:
            logger.warning("No user in initData")
            return None
        
        # user приходит как URL-encoded JSON
        user_data = json.loads(unquote(user_json))
        
        return UserFromTelegram(
            id=user_data.get("id"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            username=user_data.get("username"),
            language_code=user_data.get("language_code"),
            is_premium=user_data.get("is_premium"),
        )
        
    except Exception as e:
        logger.error(f"Error parsing user from initData: {e}")
        return None

