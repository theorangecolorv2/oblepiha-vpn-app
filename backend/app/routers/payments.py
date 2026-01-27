"""
API для платежей.
Создание платежей, webhook от YooKassa, история.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_tariff_by_id, REFERRAL_BONUS_DAYS, REFERRAL_QUALIFYING_TARIFFS
from app.database import get_db
from app.middleware.auth import get_current_user, TelegramUser
from app.models.user import User
from app.models.payment import Payment
from app.models.referral import ReferralReward
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentHistoryItem
from app.services.remnawave import get_remnawave_service, RemnawaveError
from app.services.yookassa_service import get_yookassa_service
from app.services.telegram_notify import send_payment_success_message, send_referral_bonus_message

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Создать платёж для покупки тарифа.
    Возвращает URL для оплаты через YooKassa.
    """
    logger.info(f"Creating payment: tariff_id={payment_data.tariff_id}, user_id={telegram_user.id}")
    yookassa = get_yookassa_service()
    
    # Проверяем тариф
    tariff = get_tariff_by_id(payment_data.tariff_id)
    if not tariff:
        raise HTTPException(status_code=400, detail="Invalid tariff_id")

    # Получаем пользователя из БД
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found. Call /api/users/me first")

    # Проверяем, не пытается ли пользователь купить пробный тариф повторно
    if payment_data.tariff_id == "trial" and user.trial_used:
        raise HTTPException(
            status_code=400,
            detail="Trial period can only be used once"
        )

    # Получаем информацию о реферере для description платежа
    referrer_username = None
    referrer_telegram_id = None
    if user.referrer_id:
        referrer_result = await db.execute(
            select(User).where(User.telegram_id == user.referrer_id)
        )
        referrer = referrer_result.scalar_one_or_none()
        if referrer:
            referrer_username = referrer.telegram_username
            referrer_telegram_id = referrer.telegram_id

    # Создаём платёж в YooKassa
    # save_payment_method=True ограничивает способы оплаты до тех, что поддерживают сохранение
    yookassa_payment = yookassa.create_payment(
        tariff_id=payment_data.tariff_id,
        telegram_id=telegram_user.id,
        user_id=user.id,
        save_payment_method=payment_data.setup_auto_renew,
        username=telegram_user.username,
        referrer_username=referrer_username,
        referrer_telegram_id=referrer_telegram_id,
    )
    
    if not yookassa_payment:
        raise HTTPException(status_code=500, detail="Failed to create payment")
    
    # Сохраняем платёж в БД
    payment = Payment(
        user_id=user.id,
        telegram_id=telegram_user.id,
        tariff_id=payment_data.tariff_id,
        tariff_name=tariff["name"],
        amount=tariff["price"] * 100,  # В копейках
        days=tariff["days"],
        yookassa_payment_id=yookassa_payment.id,
        status="pending",
        metadata_json=json.dumps({
            "yookassa_status": yookassa_payment.status,
        }),
    )
    db.add(payment)
    await db.commit()
    
    # Получаем URL для оплаты
    confirmation_url = yookassa_payment.confirmation.confirmation_url
    
    return PaymentResponse(
        payment_id=yookassa_payment.id,
        confirmation_url=confirmation_url,
        amount=tariff["price"],
        tariff_id=tariff["id"],
        tariff_name=tariff["name"],
    )


@router.post("/webhook")
async def yookassa_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Webhook для обработки уведомлений от YooKassa.
    
    YooKassa отправляет уведомления о изменении статуса платежа.
    При успешной оплате продлеваем подписку в Remnawave.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    logger.info(f"YooKassa webhook received: {body}")
    
    event_type = body.get("event")
    payment_object = body.get("object", {})
    payment_id = payment_object.get("id")
    
    if not payment_id:
        raise HTTPException(status_code=400, detail="Missing payment id")
    
    # Находим платёж в БД
    result = await db.execute(
        select(Payment).where(Payment.yookassa_payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        logger.warning(f"Payment not found in DB: {payment_id}")
        return {"status": "ok"}  # Отвечаем OK чтобы YooKassa не повторяла
    
    new_status = payment_object.get("status", "unknown")
    
    # Обновляем статус платежа
    payment.status = new_status
    payment.metadata_json = json.dumps(payment_object)
    
    # Если платёж успешен - продлеваем подписку
    if new_status == "succeeded" and payment_object.get("paid"):
        logger.info(f"Payment succeeded: {payment_id}, extending subscription")

        payment.paid_at = datetime.utcnow()

        # Сохраняем payment_method_id если карта была сохранена
        payment_method = payment_object.get("payment_method", {})
        if payment_method.get("saved"):
            payment_method_id = payment_method.get("id")
            if payment_method_id:
                payment.payment_method_id = payment_method_id
                logger.info(f"Saved payment_method_id: {payment_method_id}")
        
        # Получаем пользователя
        user_result = await db.execute(
            select(User).where(User.id == payment.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User not found for payment: user_id={payment.user_id}")
            await db.commit()
            return {"status": "ok"}
        
        logger.info(f"Found user: telegram_id={user.telegram_id}, remnawave_uuid={user.remnawave_uuid}")
        
        remnawave = get_remnawave_service()
        
        # Если нет remnawave_uuid - пробуем найти в Remnawave
        # ВАЖНО: Ищем ТОЛЬКО по username oblepiha_*, чтобы не найти пользователя из другого сервиса!
        if not user.remnawave_uuid:
            logger.warning(f"No remnawave_uuid for user {user.telegram_id}, trying to find Oblepiha user in Remnawave")
            
            remnawave_user = None
            
            # Пробуем формат oblepiha_{telegram_id}_{username}
            if user.telegram_username:
                try:
                    full_username = f"oblepiha_{user.telegram_id}_{user.telegram_username}"
                    remnawave_user = await remnawave.get_user_by_username(full_username)
                    if remnawave_user:
                        logger.info(f"Found Oblepiha user by full username {full_username}: {remnawave_user.get('uuid')}")
                except RemnawaveError as e:
                    logger.warning(f"Failed to find by full username: {e}")
            
            # Пробуем короткий формат oblepiha_{telegram_id}
            if not remnawave_user:
                try:
                    short_username = f"oblepiha_{user.telegram_id}"
                    remnawave_user = await remnawave.get_user_by_username(short_username)
                    if remnawave_user:
                        logger.info(f"Found Oblepiha user by short username {short_username}: {remnawave_user.get('uuid')}")
                except RemnawaveError as e:
                    logger.warning(f"Failed to find by short username: {e}")
            
            # Пробуем формат с прочерком oblepiha_{telegram_id}_-
            if not remnawave_user:
                try:
                    dash_username = f"oblepiha_{user.telegram_id}_-"
                    remnawave_user = await remnawave.get_user_by_username(dash_username)
                    if remnawave_user:
                        logger.info(f"Found Oblepiha user by dash username {dash_username}: {remnawave_user.get('uuid')}")
                except RemnawaveError as e:
                    logger.warning(f"Failed to find by dash username: {e}")
            
            if remnawave_user:
                user.remnawave_uuid = remnawave_user.get("uuid")
            else:
                logger.error(f"Remnawave user not found for telegram_id={user.telegram_id}")
        
        if user.remnawave_uuid:
            try:
                remnawave_result = await remnawave.update_user_expiration(
                    uuid=user.remnawave_uuid,
                    days_to_add=payment.days,
                )

                # Обновляем статус в локальной БД
                user.is_active = True

                # Обновляем дату истечения подписки из ответа Remnawave
                if remnawave_result and remnawave_result.get("expireAt"):
                    try:
                        expire_str = remnawave_result["expireAt"]
                        user.subscription_expires_at = datetime.fromisoformat(
                            expire_str.replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                        logger.info(f"Updated subscription_expires_at for user {user.telegram_id}: {user.subscription_expires_at}")
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to parse expireAt from Remnawave: {e}")

                # Отмечаем использование пробного периода если это был trial
                if payment.tariff_id == "trial":
                    user.trial_used = True
                    logger.info(f"Trial period marked as used for user {user.telegram_id}")

                # Сохраняем данные способа оплаты если он был сохранён
                # Если пользователь согласился сохранить способ оплаты на странице ЮКассы - включаем автопродление
                if payment_method.get("saved") and payment_method_id:
                    user.payment_method_id = payment_method_id
                    payment_type = payment_method.get("type")
                    user.payment_method_type = payment_type

                    # Сохраняем данные в зависимости от типа
                    if payment_type == "bank_card":
                        card_info = payment_method.get("card", {})
                        if card_info:
                            user.card_last4 = card_info.get("last4")
                            user.card_brand = card_info.get("card_type")
                        user.sbp_phone = None
                    elif payment_type == "sbp":
                        # Для СБП: сохраняем телефон если есть
                        sbp_info = payment_method.get("sbp", {})
                        phone = sbp_info.get("phone")
                        if phone:
                            # Маскируем телефон: +7***1234
                            user.sbp_phone = phone[-4:] if len(phone) >= 4 else phone
                        user.card_last4 = None
                        user.card_brand = None
                    elif payment_type in ("sber_pay", "tinkoff_bank", "yoo_money", "mir_pay"):
                        # Для кошельков/банков - просто сохраняем тип
                        user.card_last4 = None
                        user.card_brand = None
                        user.sbp_phone = None

                    # Автоматически включаем автопродление при сохранении способа оплаты
                    user.auto_renew_enabled = True
                    logger.info(f"Payment method saved (type={payment_type}), auto-renew enabled for user {user.telegram_id}")

                logger.info(
                    f"Subscription extended: user={user.telegram_id}, days={payment.days}"
                )

                # Отправляем уведомление пользователю
                await send_payment_success_message(
                    telegram_id=user.telegram_id,
                    days=payment.days,
                    tariff_name=payment.tariff_name,
                )

                # === РЕФЕРАЛЬНЫЙ БОНУС ===
                # Условия: тариф не trial, у пользователя есть referrer_id, бонус ещё не начислялся
                if (
                    payment.tariff_id in REFERRAL_QUALIFYING_TARIFFS
                    and user.referrer_id
                ):
                    # Проверяем, не начислялся ли уже бонус за этого реферала
                    existing_reward = await db.execute(
                        select(ReferralReward).where(ReferralReward.referred_user_id == user.id)
                    )
                    if not existing_reward.scalar_one_or_none():
                        # Находим реферера
                        referrer_result = await db.execute(
                            select(User).where(User.telegram_id == user.referrer_id)
                        )
                        referrer = referrer_result.scalar_one_or_none()

                        if referrer and referrer.remnawave_uuid:
                            try:
                                # Начисляем бонус рефереру в Remnawave
                                await remnawave.update_user_expiration(
                                    uuid=referrer.remnawave_uuid,
                                    days_to_add=REFERRAL_BONUS_DAYS,
                                )

                                # Записываем в таблицу бонусов
                                reward = ReferralReward(
                                    referrer_user_id=referrer.id,
                                    referred_user_id=user.id,
                                    payment_id=payment.id,
                                    bonus_days=REFERRAL_BONUS_DAYS,
                                )
                                db.add(reward)

                                # Отправляем уведомление рефереру
                                await send_referral_bonus_message(
                                    telegram_id=referrer.telegram_id,
                                    referred_name=user.first_name or user.telegram_username or "Друг",
                                    bonus_days=REFERRAL_BONUS_DAYS,
                                )

                                logger.info(
                                    f"Referral bonus granted: +{REFERRAL_BONUS_DAYS} days to user {referrer.telegram_id} "
                                    f"for referral {user.telegram_id}"
                                )

                            except RemnawaveError as e:
                                logger.error(f"Failed to grant referral bonus: {e}")
                        else:
                            logger.warning(
                                f"Cannot grant referral bonus: referrer {user.referrer_id} not found or no remnawave_uuid"
                            )

            except RemnawaveError as e:
                logger.error(f"Failed to extend subscription in Remnawave: {e}")
                # Платёж прошёл, но Remnawave не обновился
                # Нужно будет обработать вручную или через retry
        else:
            logger.error(f"Cannot extend subscription: no remnawave_uuid for user {user.telegram_id}")
    
    await db.commit()
    
    return {"status": "ok"}


@router.get("/history", response_model=list[PaymentHistoryItem])
async def get_payment_history(
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
):
    """Получить историю платежей пользователя"""
    result = await db.execute(
        select(Payment)
        .where(Payment.telegram_id == telegram_user.id)
        .order_by(Payment.created_at.desc())
        .limit(limit)
    )
    payments = result.scalars().all()
    
    return [
        PaymentHistoryItem(
            id=p.id,
            tariff_name=p.tariff_name,
            amount=p.amount // 100,  # Из копеек в рубли
            days=p.days,
            status=p.status,
            created_at=p.created_at,
            paid_at=p.paid_at,
        )
        for p in payments
    ]


@router.get("/{payment_id}/status")
async def get_payment_status(
    payment_id: str,
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Проверить статус конкретного платежа"""
    result = await db.execute(
        select(Payment)
        .where(
            Payment.yookassa_payment_id == payment_id,
            Payment.telegram_id == telegram_user.id,
        )
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Также проверяем статус в YooKassa
    yookassa = get_yookassa_service()
    yookassa_payment = yookassa.get_payment(payment_id)
    
    actual_status = payment.status
    if yookassa_payment:
        actual_status = yookassa_payment.status
        
        # Обновляем локальный статус если изменился
        if actual_status != payment.status:
            payment.status = actual_status
            await db.commit()
    
    return {
        "payment_id": payment_id,
        "status": actual_status,
        "paid": actual_status == "succeeded",
    }

