"""
Pydantic схемы для пользователей.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


# Базовый конфиг для camelCase сериализации
camel_config = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    by_alias=True,
)


class UserFromTelegram(BaseModel):
    """Данные пользователя из Telegram initData"""
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None


class UserCreate(BaseModel):
    """Создание пользователя"""
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    """Ответ с данными пользователя"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        by_alias=True,
        from_attributes=True,
    )
    
    id: int
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    
    # Статус подписки
    is_active: bool = False
    subscription_expires_at: Optional[datetime] = None
    days_left: int = 0
    
    # VPN данные
    subscription_url: Optional[str] = None
    
    # Трафик (из Remnawave)
    traffic_used_bytes: int = 0
    traffic_limit_bytes: int = 0
    
    # Реферальная система
    referral_code: Optional[str] = None


class UserStatsResponse(BaseModel):
    """Статистика пользователя для главного экрана"""
    model_config = camel_config
    
    is_active: bool = False
    days_left: int = 0
    total_days: int = 30
    traffic_left_gb: float = 0
    total_traffic_gb: float = 200
    subscription_url: Optional[str] = None

