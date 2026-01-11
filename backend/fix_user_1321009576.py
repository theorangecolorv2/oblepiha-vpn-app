"""
Скрипт для починки пользователя 1321009576 (@i_n_f_i_n_i_t_y_197).

Проблема: Username был слишком длинным (44 символа), Remnawave отклонил создание.
Пользователь оплатил trial (10₽), но подписка не активировалась.

Запуск: cd /opt/oblepiha-vpn-app/backend && python fix_user_1321009576.py
"""

import asyncio
import os
import sys

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Импортируем после добавления в path
from app.config import get_settings
from app.models.user import User


async def main():
    settings = get_settings()

    # Данные пользователя
    TELEGRAM_ID = 1321009576
    USERNAME = f"oblepiha_{TELEGRAM_ID}"  # Короткий username (20 символов)
    DAYS_TO_ADD = 7  # Trial + 4 дня компенсации

    print(f"=== Починка пользователя {TELEGRAM_ID} ===")
    print(f"Username для Remnawave: {USERNAME} ({len(USERNAME)} символов)")

    # Подключаемся к БД
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    headers = {
        "Authorization": f"Bearer {settings.remnawave_api_token}",
        "Content-Type": "application/json",
    }
    base_url = settings.remnawave_api_url.rstrip("/")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Проверяем, нет ли уже пользователя в Remnawave
        print("\n1. Проверяем существование в Remnawave...")

        try:
            resp = await client.get(
                f"{base_url}/api/users/by-username/{USERNAME}",
                headers=headers
            )
            if resp.status_code == 200:
                existing = resp.json().get("response")
                print(f"   Пользователь уже существует: {existing.get('uuid')}")
                remnawave_uuid = existing.get("uuid")
                subscription_url = existing.get("subscriptionUrl")
            else:
                existing = None
        except Exception as e:
            print(f"   Ошибка проверки: {e}")
            existing = None

        # 2. Если не существует - создаём
        if not existing:
            print("\n2. Создаём пользователя в Remnawave...")

            # Дата в прошлом (подписка неактивна, потом продлим)
            expire_at = datetime.utcnow() - timedelta(days=1)

            payload = {
                "username": USERNAME,
                "telegramId": TELEGRAM_ID,
                "status": "ACTIVE",
                "expireAt": expire_at.isoformat() + "Z",
                "trafficLimitBytes": settings.remnawave_traffic_limit_bytes,
                "trafficLimitStrategy": settings.remnawave_traffic_reset_strategy,
                "hwidDeviceLimit": settings.remnawave_hwid_device_limit,
                "activeInternalSquads": [settings.remnawave_squad_id],
            }

            if settings.remnawave_external_squad_id:
                payload["externalSquadUuid"] = settings.remnawave_external_squad_id

            resp = await client.post(
                f"{base_url}/api/users",
                headers=headers,
                json=payload
            )

            if resp.status_code >= 400:
                print(f"   ОШИБКА создания: {resp.status_code} - {resp.text}")
                return

            created = resp.json().get("response")
            remnawave_uuid = created.get("uuid")
            subscription_url = created.get("subscriptionUrl")
            print(f"   Создан: uuid={remnawave_uuid}")

        # 3. Продлеваем подписку
        print(f"\n3. Продлеваем подписку на {DAYS_TO_ADD} дней...")

        new_expire = datetime.utcnow() + timedelta(days=DAYS_TO_ADD)

        extend_payload = {
            "uuid": remnawave_uuid,
            "expireAt": new_expire.isoformat() + "Z",
            "status": "ACTIVE",
        }

        resp = await client.patch(
            f"{base_url}/api/users",
            headers=headers,
            json=extend_payload
        )

        if resp.status_code >= 400:
            print(f"   ОШИБКА продления: {resp.status_code} - {resp.text}")
            return

        updated = resp.json().get("response")
        subscription_url = updated.get("subscriptionUrl") or subscription_url
        print(f"   Подписка продлена до: {new_expire}")
        print(f"   Subscription URL: {subscription_url}")

        # 4. Обновляем БД
        print("\n4. Обновляем локальную БД...")

        async with async_session() as db:
            result = await db.execute(
                update(User)
                .where(User.telegram_id == TELEGRAM_ID)
                .values(
                    remnawave_uuid=remnawave_uuid,
                    remnawave_username=USERNAME,
                    subscription_url=subscription_url,
                    is_active=True,
                )
            )
            await db.commit()
            print(f"   Обновлено записей: {result.rowcount}")

        print("\n=== ГОТОВО ===")
        print(f"Пользователь @i_n_f_i_n_i_t_y_197 (telegram_id={TELEGRAM_ID}) починен!")
        print(f"UUID: {remnawave_uuid}")
        print(f"Подписка до: {new_expire}")


if __name__ == "__main__":
    asyncio.run(main())
