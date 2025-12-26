"""
Задача автоматического продления подписок.

Для пользователей с включённым автопродлением:
1. Создаёт платёж в YooKassa по сохранённому payment_method_id
2. При успехе: продлевает подписку в Remnawave
3. При ошибке: уведомляет пользователя, повторяет через 6 часов (до 3 попыток)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta

from sqlalchemy import select, and_

from app.config import get_tariff_by_id
from app.database import async_session_maker
from app.models.user import User
from app.models.payment import Payment
from app.services.remnawave import get_remnawave_service, RemnawaveError
from app.services.yookassa_service import get_yookassa_service
from app.services.telegram_notify import (
    send_auto_renew_success,
    send_auto_renew_failed,
)

logger = logging.getLogger(__name__)

# Тариф для автопродления (месяц)
AUTO_RENEW_TARIFF_ID = "month"
AUTO_RENEW_AMOUNT = 199
AUTO_RENEW_DAYS = 30

# Максимум попыток автоплатежа
MAX_ATTEMPTS = 3

# Пауза между обработками пользователей
PROCESS_DELAY_MS = 100


async def process_auto_renewals() -> None:
    """
    Обработать автопродления подписок.

    Критерии выборки:
    - auto_renew_enabled = True
    - payment_method_id IS NOT NULL
    - subscription_expires_at между NOW - 1 час и NOW + 1 час
    - Нет успешного автоплатежа за последние 24 часа

    Логика:
    1. Создаём платёж в YooKassa (без подтверждения)
    2. Если успешно - продлеваем в Remnawave, уведомляем
    3. Если ошибка - уведомляем, ставим retry через 6 часов
    """
    logger.info("Starting auto-renewal task...")

    now = datetime.utcnow()
    window_start = now - timedelta(hours=1)
    window_end = now + timedelta(hours=1)
    recent_payment_threshold = now - timedelta(hours=24)

    success_count = 0
    failed_count = 0
    skipped_count = 0

    yookassa = get_yookassa_service()
    remnawave = get_remnawave_service()

    try:
        async with async_session_maker() as db:
            # Находим пользователей для автопродления
            result = await db.execute(
                select(User).where(
                    and_(
                        User.auto_renew_enabled == True,
                        User.payment_method_id.isnot(None),
                        User.subscription_expires_at.isnot(None),
                        User.subscription_expires_at >= window_start,
                        User.subscription_expires_at <= window_end,
                    )
                )
            )
            users = result.scalars().all()

            logger.info(f"Found {len(users)} users eligible for auto-renewal")

            for user in users:
                try:
                    # Проверяем, не было ли уже успешного автоплатежа за 24 часа
                    recent_payment = await db.execute(
                        select(Payment).where(
                            and_(
                                Payment.user_id == user.id,
                                Payment.is_auto_payment == True,
                                Payment.status == "succeeded",
                                Payment.created_at > recent_payment_threshold,
                            )
                        )
                    )
                    if recent_payment.scalar_one_or_none():
                        logger.debug(
                            f"Skipping user {user.telegram_id}: "
                            "recent successful auto-payment exists"
                        )
                        skipped_count += 1
                        continue

                    # Проверяем количество неудачных попыток за 24 часа
                    failed_attempts = await db.execute(
                        select(Payment).where(
                            and_(
                                Payment.user_id == user.id,
                                Payment.is_auto_payment == True,
                                Payment.status == "canceled",
                                Payment.created_at > recent_payment_threshold,
                            )
                        )
                    )
                    failed_count_for_user = len(failed_attempts.scalars().all())

                    if failed_count_for_user >= MAX_ATTEMPTS:
                        logger.debug(
                            f"Skipping user {user.telegram_id}: "
                            f"max attempts ({MAX_ATTEMPTS}) reached"
                        )
                        skipped_count += 1
                        continue

                    logger.info(
                        f"Processing auto-renewal for user {user.telegram_id}, "
                        f"attempt {failed_count_for_user + 1}/{MAX_ATTEMPTS}"
                    )

                    # Создаём автоплатёж
                    yookassa_payment = yookassa.create_auto_payment(
                        payment_method_id=user.payment_method_id,
                        amount=AUTO_RENEW_AMOUNT,
                        telegram_id=user.telegram_id,
                        user_id=user.id,
                        days=AUTO_RENEW_DAYS,
                    )

                    if not yookassa_payment:
                        logger.error(
                            f"Failed to create auto-payment for user {user.telegram_id}"
                        )
                        # Создаём запись о неудачной попытке
                        payment = Payment(
                            user_id=user.id,
                            telegram_id=user.telegram_id,
                            tariff_id=AUTO_RENEW_TARIFF_ID,
                            tariff_name="Автопродление",
                            amount=AUTO_RENEW_AMOUNT * 100,
                            days=AUTO_RENEW_DAYS,
                            status="canceled",
                            is_auto_payment=True,
                            auto_payment_attempt=failed_count_for_user + 1,
                            metadata_json=json.dumps({"error": "Failed to create payment"}),
                        )
                        db.add(payment)
                        failed_count += 1

                        await send_auto_renew_failed(
                            telegram_id=user.telegram_id,
                            reason="payment_creation_failed",
                            card_last4=user.card_last4,
                        )
                        continue

                    # Сохраняем платёж в БД
                    payment = Payment(
                        user_id=user.id,
                        telegram_id=user.telegram_id,
                        tariff_id=AUTO_RENEW_TARIFF_ID,
                        tariff_name="Автопродление",
                        amount=AUTO_RENEW_AMOUNT * 100,
                        days=AUTO_RENEW_DAYS,
                        yookassa_payment_id=yookassa_payment.id,
                        payment_method_id=user.payment_method_id,
                        status=yookassa_payment.status,
                        is_auto_payment=True,
                        auto_payment_attempt=failed_count_for_user + 1,
                        metadata_json=json.dumps({
                            "auto_payment": True,
                            "yookassa_status": yookassa_payment.status,
                        }),
                    )
                    db.add(payment)

                    # Проверяем статус платежа
                    if yookassa_payment.status == "succeeded" and yookassa_payment.paid:
                        payment.paid_at = datetime.utcnow()

                        # Продлеваем подписку в Remnawave
                        if user.remnawave_uuid:
                            try:
                                await remnawave.update_user_expiration(
                                    uuid=user.remnawave_uuid,
                                    days_to_add=AUTO_RENEW_DAYS,
                                )
                                user.is_active = True

                                logger.info(
                                    f"Auto-renewal successful for user {user.telegram_id}"
                                )
                                success_count += 1

                                await send_auto_renew_success(
                                    telegram_id=user.telegram_id,
                                    days=AUTO_RENEW_DAYS,
                                    amount=AUTO_RENEW_AMOUNT,
                                    card_last4=user.card_last4,
                                )

                            except RemnawaveError as e:
                                logger.error(
                                    f"Failed to extend subscription in Remnawave "
                                    f"for user {user.telegram_id}: {e}"
                                )
                                # Платёж прошёл, но Remnawave не обновился
                                # Это критично - нужно уведомить и обработать вручную
                                failed_count += 1
                        else:
                            logger.error(
                                f"No remnawave_uuid for user {user.telegram_id}"
                            )
                            success_count += 1  # Платёж прошёл

                    elif yookassa_payment.status == "canceled":
                        # Платёж отклонён
                        cancellation_details = getattr(
                            yookassa_payment, "cancellation_details", None
                        )
                        reason = "unknown"
                        if cancellation_details:
                            reason = getattr(cancellation_details, "reason", "unknown")

                        logger.warning(
                            f"Auto-payment canceled for user {user.telegram_id}, "
                            f"reason: {reason}"
                        )
                        failed_count += 1

                        await send_auto_renew_failed(
                            telegram_id=user.telegram_id,
                            reason=reason,
                            card_last4=user.card_last4,
                        )

                    else:
                        # Статус pending или waiting_for_capture
                        # Webhook обработает когда придёт
                        logger.info(
                            f"Auto-payment pending for user {user.telegram_id}, "
                            f"status: {yookassa_payment.status}"
                        )

                    # Пауза между пользователями
                    await asyncio.sleep(PROCESS_DELAY_MS / 1000)

                except Exception as e:
                    logger.error(
                        f"Error processing auto-renewal for user {user.telegram_id}: {e}"
                    )
                    failed_count += 1

            # Сохраняем все изменения
            await db.commit()

    except Exception as e:
        logger.error(f"Auto-renewal task failed: {e}")
        raise

    logger.info(
        f"Auto-renewal completed: "
        f"success={success_count}, failed={failed_count}, skipped={skipped_count}"
    )
