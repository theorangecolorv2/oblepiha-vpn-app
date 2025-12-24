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
        try:
            username = f"tg_{telegram_user.id}"
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
            # Пользователь может уже существовать в Remnawave
            # Пробуем найти по telegram_id
            try:
                existing = await remnawave.get_user_by_telegram_id(telegram_user.id)
                if existing:
                    user.remnawave_uuid = existing.get("uuid")
                    user.remnawave_username = existing.get("username")
                    user.subscription_url = existing.get("subscriptionUrl")
            except Exception as inner_e:
                logger.error(f"Failed to find existing Remnawave user: {inner_e}")
        
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
            total_traffic_gb=200,
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
        traffic_limit_gb = traffic_limit / (1024 ** 3) if traffic_limit > 0 else 200
        traffic_left_gb = max(0, traffic_limit_gb - traffic_used_gb)
        
        return UserStatsResponse(
            is_active=is_active,
            days_left=days_left,
            total_days=total_days,
            traffic_left_gb=round(traffic_left_gb, 1),
            total_traffic_gb=round(traffic_limit_gb, 1) if traffic_limit > 0 else 200,
            subscription_url=user.subscription_url,
        )
        
    except RemnawaveError as e:
        logger.error(f"Failed to get stats from Remnawave: {e}")
        return UserStatsResponse()

