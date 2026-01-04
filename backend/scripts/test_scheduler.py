#!/usr/bin/env python3
"""
Скрипт для тестирования задач scheduler.

Позволяет вручную запустить:
- Синхронизацию с Remnawave
- Уведомления об истечении подписки
- Автопродления

Запуск:
    cd backend

    # Запустить все задачи
    python scripts/test_scheduler.py --all

    # Только синхронизация
    python scripts/test_scheduler.py --sync

    # Только уведомления
    python scripts/test_scheduler.py --notify

    # Только автопродления
    python scripts/test_scheduler.py --auto-renew

    # Состарить подписку пользователя (для тестов)
    python scripts/test_scheduler.py --age-subscription --telegram-id 123456789 --minutes 30
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем путь к приложению
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database import async_session_maker, init_db
from app.models.user import User


async def run_sync():
    """Запустить синхронизацию с Remnawave."""
    from app.scheduler.tasks.sync_remnawave import sync_users_with_remnawave
    print("=" * 60)
    print("SYNC WITH REMNAWAVE")
    print("=" * 60)
    await sync_users_with_remnawave()
    print()


async def run_notify():
    """Запустить уведомления об истечении."""
    from app.scheduler.tasks.expiration_notify import send_expiration_notifications
    print("=" * 60)
    print("EXPIRATION NOTIFICATIONS")
    print("=" * 60)
    await send_expiration_notifications()
    print()


async def run_auto_renew():
    """Запустить автопродления."""
    from app.scheduler.tasks.auto_renew import process_auto_renewals
    print("=" * 60)
    print("AUTO-RENEWALS")
    print("=" * 60)
    await process_auto_renewals()
    print()


async def age_subscription(telegram_id: int, minutes: int):
    """
    Состарить подписку пользователя для тестирования.

    Устанавливает subscription_expires_at на указанное количество минут от сейчас.
    """
    print("=" * 60)
    print(f"AGE SUBSCRIPTION FOR USER {telegram_id}")
    print("=" * 60)

    await init_db()

    async with async_session_maker() as db:
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            print(f"Пользователь с telegram_id={telegram_id} не найден!")
            return

        old_expires_at = user.subscription_expires_at
        new_expires_at = datetime.utcnow() + timedelta(minutes=minutes)

        print(f"Пользователь: {user.telegram_id}")
        print(f"auto_renew_enabled: {user.auto_renew_enabled}")
        print(f"payment_method_id: {user.payment_method_id}")
        print(f"card_last4: {user.card_last4}")
        print()
        print(f"Старое время истечения: {old_expires_at}")
        print(f"Новое время истечения:  {new_expires_at}")
        print(f"(через {minutes} минут от сейчас)")

        user.subscription_expires_at = new_expires_at
        await db.commit()

        print()
        print("Подписка успешно состарена!")
        print()
        print("Теперь можно запустить:")
        print("  python scripts/test_scheduler.py --auto-renew")
        print("  python scripts/test_scheduler.py --notify")


async def show_user_info(telegram_id: int):
    """Показать информацию о пользователе."""
    print("=" * 60)
    print(f"USER INFO: {telegram_id}")
    print("=" * 60)

    await init_db()

    async with async_session_maker() as db:
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            print(f"Пользователь с telegram_id={telegram_id} не найден!")
            return

        now = datetime.utcnow()
        expires_at = user.subscription_expires_at

        print(f"ID в БД:                 {user.id}")
        print(f"Telegram ID:             {user.telegram_id}")
        print(f"Remnawave UUID:          {user.remnawave_uuid}")
        print(f"is_active:               {user.is_active}")
        print(f"subscription_expires_at: {expires_at}")

        if expires_at:
            delta = expires_at - now
            if delta.total_seconds() > 0:
                print(f"                         (через {delta})")
            else:
                print(f"                         (истекла {-delta} назад)")

        print()
        print(f"auto_renew_enabled:      {user.auto_renew_enabled}")
        print(f"payment_method_id:       {user.payment_method_id}")
        print(f"card_last4:              {user.card_last4}")
        print(f"terms_accepted_at:       {user.terms_accepted_at}")
        print(f"trial_used:              {user.trial_used}")


async def main():
    parser = argparse.ArgumentParser(
        description="Тестирование задач scheduler"
    )
    parser.add_argument("--all", action="store_true", help="Запустить все задачи")
    parser.add_argument("--sync", action="store_true", help="Синхронизация с Remnawave")
    parser.add_argument("--notify", action="store_true", help="Уведомления об истечении")
    parser.add_argument("--auto-renew", action="store_true", help="Автопродления")
    parser.add_argument(
        "--age-subscription",
        action="store_true",
        help="Состарить подписку пользователя"
    )
    parser.add_argument(
        "--user-info",
        action="store_true",
        help="Показать информацию о пользователе"
    )
    parser.add_argument(
        "--telegram-id",
        type=int,
        help="Telegram ID пользователя"
    )
    parser.add_argument(
        "--minutes",
        type=int,
        default=30,
        help="Через сколько минут истечёт подписка (по умолчанию: 30)"
    )

    args = parser.parse_args()

    # Инициализируем БД для всех операций
    await init_db()

    if args.user_info:
        if not args.telegram_id:
            print("Укажите --telegram-id")
            sys.exit(1)
        await show_user_info(args.telegram_id)
        return

    if args.age_subscription:
        if not args.telegram_id:
            print("Укажите --telegram-id")
            sys.exit(1)
        await age_subscription(args.telegram_id, args.minutes)
        return

    if args.all:
        await run_sync()
        await run_notify()
        await run_auto_renew()
        return

    if args.sync:
        await run_sync()

    if args.notify:
        await run_notify()

    if args.auto_renew:
        await run_auto_renew()

    if not any([args.all, args.sync, args.notify, args.auto_renew]):
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
