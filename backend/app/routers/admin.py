"""
Роутер для админ-панели.
Все эндпоинты требуют проверки админского доступа.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ADMIN_IDS
from app.database import get_db
from app.middleware.auth import TelegramUser, get_current_user
from app.models.user import User
from app.models.payment import Payment


router = APIRouter(prefix="/api/admin", tags=["admin"])

# Московское время UTC+3
MSK = timezone(timedelta(hours=3))


def get_msk_today_bounds() -> tuple[datetime, datetime, datetime]:
    """Возвращает начало сегодня, начало завтра и начало послезавтра по МСК"""
    now_msk = datetime.now(MSK)
    today_start_msk = now_msk.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start_msk = today_start_msk + timedelta(days=1)
    day_after_tomorrow_msk = today_start_msk + timedelta(days=2)

    # Конвертируем в UTC (naive datetime для SQLite)
    today_start_utc = today_start_msk.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow_start_utc = tomorrow_start_msk.astimezone(timezone.utc).replace(tzinfo=None)
    day_after_tomorrow_utc = day_after_tomorrow_msk.astimezone(timezone.utc).replace(tzinfo=None)

    return today_start_utc, tomorrow_start_utc, day_after_tomorrow_utc


async def require_admin(user: TelegramUser = Depends(get_current_user)) -> TelegramUser:
    """Dependency для проверки админского доступа"""
    if user.id not in ADMIN_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


# === Схемы ===

class AdminMeResponse(BaseModel):
    id: int
    first_name: str
    is_admin: bool = True


class TopReferrer(BaseModel):
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    referral_count: int


class StatsResponse(BaseModel):
    # Основные
    active_subscriptions: int
    new_users_today: int
    trials_today: int
    expiring_today: int
    expiring_tomorrow: int

    # Дополнительные
    auto_renew_enabled: int
    channel_bonus_today: int
    channel_bonus_total: int
    referrals_total: int
    top_referrers: list[TopReferrer]

    # Конверсия
    trial_users_total: int
    trial_converted: int
    trial_conversion_percent: float

    # Мета
    total_users: int
    generated_at: str


# === Эндпоинты ===

@router.get("/me", response_model=AdminMeResponse)
async def admin_me(admin: TelegramUser = Depends(require_admin)):
    """Проверка админского доступа"""
    return AdminMeResponse(
        id=admin.id,
        first_name=admin.first_name or "Admin"
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    admin: TelegramUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику для админ-панели"""

    today_start, tomorrow_start, day_after_tomorrow = get_msk_today_bounds()
    now = datetime.utcnow()

    # === Основные метрики ===

    # Активные подписки
    active_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active == True)
    )
    active_subscriptions = active_result.scalar() or 0

    # Новые юзеры сегодня
    new_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.created_at >= today_start)
    )
    new_users_today = new_users_result.scalar() or 0

    # Триалы сегодня (оплаченные)
    trials_result = await db.execute(
        select(func.count()).select_from(Payment).where(
            and_(
                Payment.tariff_id == "trial",
                Payment.status == "succeeded",
                Payment.paid_at >= today_start
            )
        )
    )
    trials_today = trials_result.scalar() or 0

    # Истекает сегодня (с текущего момента до 00:00 МСК завтра)
    expiring_today_result = await db.execute(
        select(func.count()).select_from(User).where(
            and_(
                User.subscription_expires_at >= now,
                User.subscription_expires_at < tomorrow_start,
                User.is_active == True
            )
        )
    )
    expiring_today = expiring_today_result.scalar() or 0

    # Истекает завтра (00:00 МСК завтра до 00:00 МСК послезавтра)
    expiring_tomorrow_result = await db.execute(
        select(func.count()).select_from(User).where(
            and_(
                User.subscription_expires_at >= tomorrow_start,
                User.subscription_expires_at < day_after_tomorrow,
                User.is_active == True
            )
        )
    )
    expiring_tomorrow = expiring_tomorrow_result.scalar() or 0

    # === Дополнительные метрики ===

    # Автопродления активны
    auto_renew_result = await db.execute(
        select(func.count()).select_from(User).where(User.auto_renew_enabled == True)
    )
    auto_renew_enabled = auto_renew_result.scalar() or 0

    # Бонусы за канал сегодня
    channel_bonus_today_result = await db.execute(
        select(func.count()).select_from(User).where(
            User.channel_bonus_received_at >= today_start
        )
    )
    channel_bonus_today = channel_bonus_today_result.scalar() or 0

    # Бонусы за канал всего
    channel_bonus_total_result = await db.execute(
        select(func.count()).select_from(User).where(
            User.channel_bonus_received_at.isnot(None)
        )
    )
    channel_bonus_total = channel_bonus_total_result.scalar() or 0

    # Рефералы (пришедшие по ссылке)
    referrals_result = await db.execute(
        select(func.count()).select_from(User).where(User.referrer_id.isnot(None))
    )
    referrals_total = referrals_result.scalar() or 0

    # Топ 5 рефереров
    top_referrers_query = (
        select(
            User.telegram_id,
            User.telegram_username,
            User.first_name,
            func.count().label("referral_count")
        )
        .select_from(User)
        .join(
            User,
            User.referrer_id == User.telegram_id,
            isouter=False
        )
        .group_by(User.telegram_id, User.telegram_username, User.first_name)
        .order_by(func.count().desc())
        .limit(5)
    )

    # Альтернативный запрос через подзапрос
    referrer_counts = (
        select(
            User.referrer_id.label("referrer_telegram_id"),
            func.count().label("cnt")
        )
        .where(User.referrer_id.isnot(None))
        .group_by(User.referrer_id)
        .subquery()
    )

    top_referrers_result = await db.execute(
        select(
            User.telegram_id,
            User.telegram_username,
            User.first_name,
            referrer_counts.c.cnt.label("referral_count")
        )
        .join(referrer_counts, User.telegram_id == referrer_counts.c.referrer_telegram_id)
        .order_by(referrer_counts.c.cnt.desc())
        .limit(5)
    )

    top_referrers = [
        TopReferrer(
            telegram_id=row.telegram_id,
            username=row.telegram_username,
            first_name=row.first_name,
            referral_count=row.referral_count
        )
        for row in top_referrers_result.all()
    ]

    # === Конверсия trial → платный ===

    # Всего юзеров с trial
    trial_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.trial_used == True)
    )
    trial_users_total = trial_users_result.scalar() or 0

    # Юзеры с trial, которые потом купили платный тариф
    # (есть succeeded платёж с tariff_id != 'trial')
    trial_converted_result = await db.execute(
        select(func.count(func.distinct(Payment.telegram_id)))
        .select_from(Payment)
        .join(User, User.telegram_id == Payment.telegram_id)
        .where(
            and_(
                User.trial_used == True,
                Payment.tariff_id != "trial",
                Payment.status == "succeeded"
            )
        )
    )
    trial_converted = trial_converted_result.scalar() or 0

    # Процент конверсии
    trial_conversion_percent = (
        round(trial_converted / trial_users_total * 100, 1)
        if trial_users_total > 0 else 0.0
    )

    # === Мета ===

    total_users_result = await db.execute(
        select(func.count()).select_from(User)
    )
    total_users = total_users_result.scalar() or 0

    return StatsResponse(
        active_subscriptions=active_subscriptions,
        new_users_today=new_users_today,
        trials_today=trials_today,
        expiring_today=expiring_today,
        expiring_tomorrow=expiring_tomorrow,
        auto_renew_enabled=auto_renew_enabled,
        channel_bonus_today=channel_bonus_today,
        channel_bonus_total=channel_bonus_total,
        referrals_total=referrals_total,
        top_referrers=top_referrers,
        trial_users_total=trial_users_total,
        trial_converted=trial_converted,
        trial_conversion_percent=trial_conversion_percent,
        total_users=total_users,
        generated_at=datetime.now(MSK).strftime("%d.%m.%Y %H:%M МСК")
    )
