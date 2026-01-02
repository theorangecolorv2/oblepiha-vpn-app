#!/usr/bin/env python3
"""Добавить mock данные карты для скриншотов"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.database import async_session_maker
from app.models.user import User
from sqlalchemy import select

async def main():
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.telegram_id == 762967142))
        user = result.scalar_one_or_none()

        if user:
            user.payment_method_id = 'demo_payment_method_12345'
            user.card_last4 = '4242'
            user.card_brand = 'Visa'
            user.auto_renew_enabled = True
            await db.commit()
            print('✅ Mock карта добавлена!')
            print(f'Карта: {user.card_brand} •••• {user.card_last4}')
            print(f'Автопродление: {user.auto_renew_enabled}')
        else:
            print('❌ Пользователь не найден')

if __name__ == '__main__':
    asyncio.run(main())
