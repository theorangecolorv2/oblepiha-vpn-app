"""
Middleware для аутентификации через Telegram initData.
"""

import logging
from typing import Optional

from fastapi import Header, HTTPException, status

from app.config import get_settings
from app.services.telegram import validate_init_data, parse_user_from_init_data
from app.schemas.user import UserFromTelegram

logger = logging.getLogger(__name__)


class TelegramUser(UserFromTelegram):
    """Аутентифицированный пользователь Telegram"""
    pass


async def get_current_user(
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data"),
) -> TelegramUser:
    """
    Dependency для получения текущего пользователя из Telegram initData.
    
    Заголовок X-Telegram-Init-Data должен содержать initData от Telegram WebApp.
    
    В dev режиме можно отключить валидацию для тестирования.
    """
    settings = get_settings()
    
    # В dev режиме разрешаем без валидации (для тестирования)
    if settings.debug and not x_telegram_init_data:
        logger.warning("Debug mode: using test user")
        return TelegramUser(
            id=123456789,
            first_name="Test",
            last_name="User",
            username="test_user",
        )
    
    if not x_telegram_init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Telegram-Init-Data header",
        )
    
    # Валидируем initData
    if not validate_init_data(x_telegram_init_data):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData",
        )
    
    # Парсим данные пользователя
    user = parse_user_from_init_data(x_telegram_init_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not parse user from initData",
        )
    
    return TelegramUser(**user.model_dump())

