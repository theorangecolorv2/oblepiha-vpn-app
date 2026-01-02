#!/usr/bin/env python3
"""Удалить mock данные карты после скриншотов"""
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
            user.payment_method_id = None
            user.card_last4 = None
            user.card_brand = None
            user.auto_renew_enabled = False
            await db.commit()
            print('✅ Mock данные удалены!')
        else:
            print('❌ Пользователь не найден')

if __name__ == '__main__':
    asyncio.run(main())
