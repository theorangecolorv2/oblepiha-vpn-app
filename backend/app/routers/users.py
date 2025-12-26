"""
API для пользователей.
Регистрация, получение данных, статистика.
"""

import logging
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, TelegramUser
from app.models.user import User
from app.schemas.user import UserResponse, UserStatsResponse
from app.services.remnawave import get_remnawave_service, RemnawaveError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["users"])


def generate_referral_code() -> str:
    """Генерация уникального реферального кода"""
    return secrets.token_urlsafe(8)[:10].upper()


@router.get("/me", response_model=UserResponse)
async def get_current_user_data(
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить данные текущего пользователя.
    Если пользователь новый - создаёт его в БД и Remnawave.
    """
    remnawave = get_remnawave_service()
    
    # Ищем пользователя в нашей БД
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Новый пользователь - создаём
        logger.info(f"Creating new user: telegram_id={telegram_user.id}")
        
        user = User(
            telegram_id=telegram_user.id,
            telegram_username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            referral_code=generate_referral_code(),
        )
        db.add(user)
        await db.flush()
        
        # Создаём пользователя в Remnawave
        # Формат: oblepiha_{telegram_id}_{username} или oblepiha_{telegram_id} если нет username
        try:
            tg_username = telegram_user.username or "-"
            username = f"oblepiha_{telegram_user.id}_{tg_username}"
            # Ограничиваем длину username (Remnawave может иметь лимит)
            if len(username) > 50:
                username = f"oblepiha_{telegram_user.id}"
            
            remnawave_user = await remnawave.create_user(
                username=username,
                telegram_id=telegram_user.id,
                expire_days=0,  # Подписка неактивна до оплаты
            )
            
            user.remnawave_uuid = remnawave_user.get("uuid")
            user.remnawave_username = username
            user.subscription_url = remnawave_user.get("subscriptionUrl")
            
        except RemnawaveError as e:
            logger.error(f"Failed to create Remnawave user: {e}")
            # Пользователь может уже существовать в Remnawave с username oblepiha_*
            # ВАЖНО: НЕ ищем по telegram_id, т.к. может найти пользователя из другого сервиса!
            existing = None
            
            # Пробуем найти по username (текущий формат oblepiha_*)
            try:
                existing = await remnawave.get_user_by_username(username)
                if existing:
                    logger.info(f"Found existing Oblepiha user by username: {existing.get('uuid')}")
            except Exception as inner_e:
                logger.warning(f"Failed to find by username: {inner_e}")
            
            # Пробуем короткий формат (без telegram username)
            if not existing:
                try:
                    short_username = f"oblepiha_{telegram_user.id}"
                    existing = await remnawave.get_user_by_username(short_username)
                    if existing:
                        logger.info(f"Found existing Oblepiha user by short username: {existing.get('uuid')}")
                except Exception as inner_e:
                    logger.warning(f"Failed to find by short username: {inner_e}")
            
            if existing:
                user.remnawave_uuid = existing.get("uuid")
                user.remnawave_username = existing.get("username")
                user.subscription_url = existing.get("subscriptionUrl")
            else:
                logger.error(f"Could not find Remnawave user for telegram_id={telegram_user.id}")
        
        await db.commit()
        await db.refresh(user)
    
    # Получаем актуальные данные из Remnawave
    traffic_used = 0
    traffic_limit = 0
    days_left = 0
    is_active = False
    subscription_expires_at = user.subscription_expires_at
    
    if user.remnawave_uuid:
        try:
            remnawave_user = await remnawave.get_user_by_uuid(user.remnawave_uuid)
            if remnawave_user:
                # Обновляем subscription_url если изменился
                new_url = remnawave_user.get("subscriptionUrl")
                if new_url and new_url != user.subscription_url:
                    user.subscription_url = new_url
                    await db.commit()
                
                # Статус подписки
                expire_at_str = remnawave_user.get("expireAt")
                if expire_at_str:
                    try:
                        expire_at = datetime.fromisoformat(expire_at_str.replace("Z", "+00:00"))
                        expire_at = expire_at.replace(tzinfo=None)
                        subscription_expires_at = expire_at
                        
                        now = datetime.utcnow()
                        if expire_at > now:
                            is_active = remnawave_user.get("status") == "ACTIVE"
                            days_left = (expire_at - now).days
                    except ValueError:
                        pass
                
                # Трафик
                traffic_data = remnawave_user.get("userTraffic", {})
                traffic_used = traffic_data.get("usedBytes", 0)
                traffic_limit = remnawave_user.get("trafficLimitBytes", 0)
                
        except RemnawaveError as e:
            logger.error(f"Failed to get Remnawave user data: {e}")
    
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        telegram_username=user.telegram_username,
        first_name=user.first_name,
        is_active=is_active,
        subscription_expires_at=subscription_expires_at,
        days_left=days_left,
        subscription_url=user.subscription_url,
        traffic_used_bytes=traffic_used,
        traffic_limit_bytes=traffic_limit,
        referral_code=user.referral_code,
        terms_accepted_at=user.terms_accepted_at,
        trial_used=user.trial_used,
        auto_renew_enabled=user.auto_renew_enabled,
        has_payment_method=bool(user.payment_method_id),
        card_last4=user.card_last4,
        card_brand=user.card_brand,
    )


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить статистику для главного экрана"""
    remnawave = get_remnawave_service()
    
    # Ищем пользователя
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.remnawave_uuid:
        return UserStatsResponse(
            is_active=False,
            days_left=0,
            total_days=30,
            traffic_left_gb=0,
            total_traffic_gb=500,
            subscription_url=None,
        )
    
    # Получаем данные из Remnawave
    try:
        remnawave_user = await remnawave.get_user_by_uuid(user.remnawave_uuid)
        if not remnawave_user:
            return UserStatsResponse()
        
        # Расчёт дней
        is_active = False
        days_left = 0
        total_days = 30
        
        expire_at_str = remnawave_user.get("expireAt")
        if expire_at_str:
            try:
                expire_at = datetime.fromisoformat(expire_at_str.replace("Z", "+00:00"))
                expire_at = expire_at.replace(tzinfo=None)
                now = datetime.utcnow()
                
                if expire_at > now:
                    is_active = remnawave_user.get("status") == "ACTIVE"
                    days_left = (expire_at - now).days
            except ValueError:
                pass
        
        # Расчёт трафика
        traffic_data = remnawave_user.get("userTraffic", {})
        traffic_used = traffic_data.get("usedBytes", 0)
        traffic_limit = remnawave_user.get("trafficLimitBytes", 0)
        
        # Конвертируем в ГБ
        traffic_used_gb = traffic_used / (1024 ** 3)
        traffic_limit_gb = traffic_limit / (1024 ** 3) if traffic_limit > 0 else 500
        traffic_left_gb = max(0, traffic_limit_gb - traffic_used_gb)
        
        return UserStatsResponse(
            is_active=is_active,
            days_left=days_left,
            total_days=total_days,
            traffic_left_gb=round(traffic_left_gb, 1),
            total_traffic_gb=round(traffic_limit_gb, 1) if traffic_limit > 0 else 500,
            subscription_url=user.subscription_url,
        )
        
    except RemnawaveError as e:
        logger.error(f"Failed to get stats from Remnawave: {e}")
        return UserStatsResponse()


@router.post("/me/accept-terms")
async def accept_terms(
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Принять условия пользования.
    Сохраняет текущее время как время принятия условий.
    """
    # Ищем пользователя
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Сохраняем время принятия условий
    user.terms_accepted_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User {telegram_user.id} accepted terms at {user.terms_accepted_at}")

    return {"status": "ok", "terms_accepted_at": user.terms_accepted_at}


@router.get("/me/auto-renew/status")
async def get_auto_renew_status(
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить статус автопродления.

    Возвращает:
    - enabled: включено ли автопродление
    - has_payment_method: есть ли сохранённый способ оплаты
    - card_last4: последние 4 цифры карты
    - card_brand: бренд карты (Visa, Mastercard, Mir)
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "enabled": user.auto_renew_enabled,
        "has_payment_method": bool(user.payment_method_id),
        "card_last4": user.card_last4,
        "card_brand": user.card_brand,
    }


@router.post("/me/auto-renew/disable")
async def disable_auto_renew(
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Отключить автопродление.

    Сохранённый способ оплаты остаётся для возможного повторного включения.
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.auto_renew_enabled = False
    await db.commit()

    logger.info(f"Auto-renew disabled for user {telegram_user.id}")

    return {"status": "ok", "auto_renew_enabled": False}


@router.post("/me/auto-renew/enable")
async def enable_auto_renew(
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Включить автопродление.

    Требует наличия сохранённого способа оплаты.
    Если способа оплаты нет - возвращает ошибку с инструкцией.
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.payment_method_id:
        raise HTTPException(
            status_code=400,
            detail="No saved payment method. Please make a payment with setup_auto_renew=true first."
        )

    user.auto_renew_enabled = True
    await db.commit()

    logger.info(f"Auto-renew enabled for user {telegram_user.id}")

    return {
        "status": "ok",
        "auto_renew_enabled": True,
        "card_last4": user.card_last4,
        "card_brand": user.card_brand,
    }


@router.delete("/me/auto-renew/payment-method")
async def delete_payment_method(
    telegram_user: TelegramUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Удалить сохранённый способ оплаты.

    Также отключает автопродление.
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.auto_renew_enabled = False
    user.payment_method_id = None
    user.card_last4 = None
    user.card_brand = None
    await db.commit()

    logger.info(f"Payment method deleted for user {telegram_user.id}")

    return {"status": "ok"}

