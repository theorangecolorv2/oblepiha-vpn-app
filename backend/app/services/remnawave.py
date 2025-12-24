"""
Клиент API Remnawave Panel.
Все операции с пользователями VPN проходят через этот сервис.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class RemnawaveError(Exception):
    """Ошибка при работе с Remnawave API"""
    def __init__(self, message: str, status_code: int = 0, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class RemnawaveService:
    """Сервис для работы с Remnawave Panel API"""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.remnawave_api_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.settings.remnawave_api_token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: dict = None,
        params: dict = None,
    ) -> dict:
        """Выполнить запрос к API"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=json_data,
                    params=params,
                )
                
                if response.status_code >= 400:
                    error_data = response.json() if response.text else {}
                    logger.error(
                        f"Remnawave API error: {response.status_code} - {error_data}"
                    )
                    raise RemnawaveError(
                        message=error_data.get("message", "Unknown error"),
                        status_code=response.status_code,
                        response_data=error_data,
                    )
                
                return response.json()
                
            except httpx.RequestError as e:
                logger.error(f"Remnawave connection error: {e}")
                raise RemnawaveError(f"Connection error: {e}")

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[dict]:
        """
        Получить пользователя по Telegram ID.
        Возвращает None если пользователь не найден.
        """
        try:
            result = await self._request(
                "GET",
                f"/api/users/by-telegram-id/{telegram_id}"
            )
            # API возвращает массив пользователей
            users = result.get("response", [])
            if users:
                return users[0]  # Берём первого (должен быть один)
            return None
        except RemnawaveError as e:
            if e.status_code == 404:
                return None
            raise

    async def get_user_by_uuid(self, uuid: str) -> Optional[dict]:
        """Получить пользователя по UUID"""
        try:
            result = await self._request("GET", f"/api/users/{uuid}")
            return result.get("response")
        except RemnawaveError as e:
            if e.status_code == 404:
                return None
            raise

    async def create_user(
        self,
        username: str,
        telegram_id: int,
        expire_days: int = 0,
        traffic_limit_bytes: int = None,
    ) -> dict:
        """
        Создать нового пользователя в Remnawave.
        
        Args:
            username: Уникальный username (используем tg_{telegram_id})
            telegram_id: Telegram ID пользователя
            expire_days: Количество дней подписки (0 = сразу истекает)
            traffic_limit_bytes: Лимит трафика (None = из настроек)
        """
        settings = self.settings
        
        # Дата истечения
        if expire_days > 0:
            expire_at = datetime.utcnow() + timedelta(days=expire_days)
        else:
            # Если дней 0, ставим дату в прошлом (подписка неактивна)
            expire_at = datetime.utcnow() - timedelta(days=1)
        
        payload = {
            "username": username,
            "telegramId": telegram_id,
            "status": "ACTIVE",
            "expireAt": expire_at.isoformat() + "Z",
            "trafficLimitBytes": traffic_limit_bytes or settings.remnawave_traffic_limit_bytes,
            "trafficLimitStrategy": settings.remnawave_traffic_reset_strategy,
            "hwidDeviceLimit": settings.remnawave_hwid_device_limit,
            "activeInternalSquads": [settings.remnawave_squad_id],
        }
        
        logger.info(f"Creating Remnawave user: {username}, telegram_id: {telegram_id}")
        
        result = await self._request("POST", "/api/users", json_data=payload)
        return result.get("response")

    async def update_user_expiration(
        self,
        uuid: str,
        days_to_add: int,
    ) -> dict:
        """
        Продлить подписку пользователя.
        
        Если подписка истекла - отсчёт от текущей даты.
        Если активна - добавляем к текущей дате истечения.
        """
        # Сначала получаем текущие данные пользователя
        user = await self.get_user_by_uuid(uuid)
        if not user:
            raise RemnawaveError(f"User not found: {uuid}", status_code=404)
        
        current_expire = user.get("expireAt")
        if current_expire:
            # Парсим текущую дату истечения
            try:
                expire_dt = datetime.fromisoformat(current_expire.replace("Z", "+00:00"))
                # Убираем timezone для сравнения
                expire_dt = expire_dt.replace(tzinfo=None)
            except ValueError:
                expire_dt = datetime.utcnow()
        else:
            expire_dt = datetime.utcnow()
        
        # Если подписка уже истекла, отсчёт от сейчас
        now = datetime.utcnow()
        if expire_dt < now:
            expire_dt = now
        
        # Добавляем дни
        new_expire = expire_dt + timedelta(days=days_to_add)
        
        payload = {
            "uuid": uuid,
            "expireAt": new_expire.isoformat() + "Z",
            "status": "ACTIVE",
        }
        
        logger.info(f"Extending subscription for {uuid}: +{days_to_add} days until {new_expire}")
        
        result = await self._request("PATCH", "/api/users", json_data=payload)
        return result.get("response")

    async def get_user_traffic(self, uuid: str) -> dict:
        """Получить информацию о трафике пользователя"""
        user = await self.get_user_by_uuid(uuid)
        if not user:
            return {"used": 0, "limit": 0}
        
        traffic = user.get("userTraffic", {})
        return {
            "used": traffic.get("usedBytes", 0),
            "limit": user.get("trafficLimitBytes", 0),
        }

    async def disable_user(self, uuid: str) -> dict:
        """Отключить пользователя"""
        result = await self._request("POST", f"/api/users/{uuid}/disable")
        return result.get("response")

    async def enable_user(self, uuid: str) -> dict:
        """Включить пользователя"""
        result = await self._request("POST", f"/api/users/{uuid}/enable")
        return result.get("response")


# Singleton instance
_remnawave_service: Optional[RemnawaveService] = None


def get_remnawave_service() -> RemnawaveService:
    """Получить экземпляр сервиса Remnawave"""
    global _remnawave_service
    if _remnawave_service is None:
        _remnawave_service = RemnawaveService()
    return _remnawave_service

