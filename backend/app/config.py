"""
Конфигурация приложения.
Все настройки загружаются из переменных окружения.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из .env"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/oblepiha.db"

    # Telegram
    telegram_bot_token: str

    # Remnawave Panel
    remnawave_api_url: str
    remnawave_api_token: str

    # Remnawave User Defaults
    remnawave_squad_id: str = "406c6e73-489d-4d38-8868-4af594bb6a86"
    remnawave_traffic_limit_bytes: int = 0
    remnawave_traffic_reset_strategy: Literal["NO_RESET", "DAY", "WEEK", "MONTH"] = "NO_RESET"
    remnawave_hwid_device_limit: int = 15

    # YooKassa
    yookassa_shop_id: str
    yookassa_secret_key: str
    yookassa_return_url: str = "https://t.me/oblepiha_bot"

    # Frontend
    frontend_url: str = "https://oblepiha-app.ru"


@lru_cache
def get_settings() -> Settings:
    """Получить настройки (кешируется)"""
    return Settings()


# Тарифы - единый источник правды
# Фронтенд получает их через API /api/tariffs
TARIFFS = [
    {
        "id": "trial",
        "name": "3 дня",
        "description": "Пробный",
        "price": 10,
        "days": 3,
        "icon": "trial",
    },
    {
        "id": "month",
        "name": "1 Месяц",
        "description": "Самый популярный",
        "price": 199,
        "days": 30,
        "icon": "month",
    },
    {
        "id": "quarter",
        "name": "3 Месяца",
        "description": "Выгодно",
        "price": 549,
        "days": 90,
        "icon": "quarter",
    },
]


def get_tariff_by_id(tariff_id: str) -> dict | None:
    """Получить тариф по ID"""
    for tariff in TARIFFS:
        if tariff["id"] == tariff_id:
            return tariff
    return None

