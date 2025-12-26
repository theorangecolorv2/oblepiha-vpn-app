"""
Задача отправки уведомлений об истечении подписки.

Отправляет уведомления пользователям, у которых подписка истекает
в течение 24 часов.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select, and_, or_

from app.database import async_session_maker
from app.models.user import User
from app.services.telegram_notify import send_expiration_warning

logger = logging.getLogger(__name__)

# Пауза между отправками (чтобы не попасть под rate limit Telegram)
SEND_DELAY_MS = 50


async def send_expiration_notifications() -> None:
    """
    Отправить уведомления об истечении подписки.

    Критерии выборки:
    - subscription_expires_at между NOW и NOW + 24 часа
    - is_active = True
    - last_notification_sent_at IS NULL или было более 23 часов назад

    Для пользователей с автопродлением - отдельный текст уведомления.
    """
    logger.info("Starting expiration notification task...")

    now = datetime.utcnow()
    expires_before = now + timedelta(hours=24)
    notification_threshold = now - timedelta(hours=23)

    sent_count = 0
    error_count = 0

    try:
        async with async_session_maker() as db:
            # Находим пользователей с истекающей подпиской
            result = await db.execute(
                select(User).where(
                    and_(
                        User.is_active == True,
                        User.subscription_expires_at.isnot(None),
                        User.subscription_expires_at > now,
                        User.subscription_expires_at <= expires_before,
                        or_(
                            User.last_notification_sent_at.is_(None),
                            User.last_notification_sent_at < notification_threshold,
                        ),
                    )
                )
            )
            users = result.scalars().all()

            logger.info(f"Found {len(users)} users to notify about expiration")

            for user in users:
                try:
                    # Считаем оставшиеся часы
                    hours_left = int(
                        (user.subscription_expires_at - now).total_seconds() / 3600
                    )

                    # Отправляем уведомление
                    success = await send_expiration_warning(
                        telegram_id=user.telegram_id,
                        hours_left=hours_left,
                        has_auto_renew=user.auto_renew_enabled,
                        card_last4=user.card_last4,
                    )

                    if success:
                        user.last_notification_sent_at = now
                        sent_count += 1
                    else:
                        error_count += 1

                    # Небольшая пауза между отправками
                    await asyncio.sleep(SEND_DELAY_MS / 1000)

                except Exception as e:
                    logger.error(
                        f"Failed to send notification to {user.telegram_id}: {e}"
                    )
                    error_count += 1

            # Сохраняем обновления last_notification_sent_at
            await db.commit()

    except Exception as e:
        logger.error(f"Expiration notification task failed: {e}")
        raise

    logger.info(
        f"Expiration notifications completed: sent={sent_count}, errors={error_count}"
    )
