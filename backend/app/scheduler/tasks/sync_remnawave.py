"""
Задача синхронизации локальной БД с Remnawave.

Источник правды: Remnawave Panel.
Синхронизируемые поля:
- subscription_expires_at (expireAt)
- is_active (status + expireAt)
"""

import asyncio
import logging
from datetime import datetime

from sqlalchemy import select

from app.database import async_session_maker
from app.models.user import User
from app.services.remnawave import get_remnawave_service, RemnawaveError

logger = logging.getLogger(__name__)

# Настройки батчинга
BATCH_SIZE = 50
REQUEST_DELAY_MS = 100  # Пауза между запросами (rate limiting)


async def sync_users_with_remnawave() -> None:
    """
    Синхронизация локальной БД с Remnawave.

    Для каждого пользователя с remnawave_uuid:
    1. Запрашиваем данные из Remnawave
    2. Обновляем subscription_expires_at и is_active
    3. Логируем изменения
    """
    logger.info("Starting Remnawave sync task...")

    remnawave = get_remnawave_service()
    synced_count = 0
    error_count = 0
    updated_count = 0

    try:
        async with async_session_maker() as db:
            # Получаем всех пользователей с remnawave_uuid
            result = await db.execute(
                select(User).where(User.remnawave_uuid.isnot(None))
            )
            users = result.scalars().all()

            logger.info(f"Found {len(users)} users to sync")

            for i, user in enumerate(users):
                try:
                    # Rate limiting
                    if i > 0 and i % BATCH_SIZE == 0:
                        await asyncio.sleep(REQUEST_DELAY_MS / 1000)
                        logger.debug(f"Processed {i}/{len(users)} users...")

                    # Запрашиваем данные из Remnawave
                    remnawave_user = await remnawave.get_user_by_uuid(user.remnawave_uuid)

                    if not remnawave_user:
                        logger.warning(
                            f"User not found in Remnawave: uuid={user.remnawave_uuid}, "
                            f"telegram_id={user.telegram_id}"
                        )
                        error_count += 1
                        continue

                    # Парсим данные
                    old_expires_at = user.subscription_expires_at
                    old_is_active = user.is_active

                    # Обновляем expireAt
                    expire_at_str = remnawave_user.get("expireAt")
                    new_expires_at = None
                    new_is_active = False

                    if expire_at_str:
                        try:
                            new_expires_at = datetime.fromisoformat(
                                expire_at_str.replace("Z", "+00:00")
                            ).replace(tzinfo=None)

                            # Проверяем активность
                            now = datetime.utcnow()
                            status = remnawave_user.get("status", "")
                            new_is_active = (
                                status == "ACTIVE" and new_expires_at > now
                            )
                        except ValueError as e:
                            logger.warning(
                                f"Failed to parse expireAt for user {user.telegram_id}: {e}"
                            )

                    # Обновляем только если есть изменения
                    if (
                        new_expires_at != old_expires_at
                        or new_is_active != old_is_active
                    ):
                        user.subscription_expires_at = new_expires_at
                        user.is_active = new_is_active
                        updated_count += 1

                        logger.debug(
                            f"Updated user {user.telegram_id}: "
                            f"expires_at {old_expires_at} -> {new_expires_at}, "
                            f"is_active {old_is_active} -> {new_is_active}"
                        )

                    synced_count += 1

                except RemnawaveError as e:
                    logger.error(
                        f"Remnawave error for user {user.telegram_id}: {e}"
                    )
                    error_count += 1
                except Exception as e:
                    logger.error(
                        f"Unexpected error syncing user {user.telegram_id}: {e}"
                    )
                    error_count += 1

            # Сохраняем все изменения
            await db.commit()

    except Exception as e:
        logger.error(f"Sync task failed with error: {e}")
        raise

    logger.info(
        f"Remnawave sync completed: "
        f"synced={synced_count}, updated={updated_count}, errors={error_count}"
    )
