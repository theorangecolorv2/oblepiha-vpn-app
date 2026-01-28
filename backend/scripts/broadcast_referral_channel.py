"""
Рассылка: реферальная программа + бонус за подписку на канал

Использование:
    # Тестовая отправка одному пользователю
    python -m scripts.broadcast_referral_channel --test 762967142

    # Рассылка всем пользователям
    python -m scripts.broadcast_referral_channel --all

    # Рассылка с задержкой между сообщениями (в секундах)
    python -m scripts.broadcast_referral_channel --all --delay 0.1
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy import select

from app.config import get_settings
from app.database import async_session_maker, init_db
from app.models.user import User

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Текст сообщения
MESSAGE_TEXT = """👥 <b>Новое: Реферальная программа!</b>

Приглашайте друзей и получайте бонусные дни или деньги. Подробности во вкладке «Рефералы».


🎁 <b>А ещё — бонус за подписку на канал</b>

Подпишитесь на @Oblepiha_Channel и получите от 1 до 5 дней подписки в подарок!"""

# Клавиатура
def get_broadcast_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Подписаться", url="https://t.me/Oblepiha_Channel"),
            InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_channel_subscription")
        ],
        [
            InlineKeyboardButton(
                text="🍊 Открыть Облепиха VPN",
                web_app=WebAppInfo(url=settings.frontend_url)
            )
        ]
    ])


async def send_to_user(bot: Bot, user_id: int) -> bool:
    """Отправить сообщение одному пользователю"""
    try:
        await bot.send_message(
            chat_id=user_id,
            text=MESSAGE_TEXT,
            reply_markup=get_broadcast_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to send to {user_id}: {e}")
        return False


async def broadcast_test(user_id: int):
    """Тестовая отправка одному пользователю"""
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    try:
        logger.info(f"Sending test message to {user_id}...")
        success = await send_to_user(bot, user_id)
        if success:
            logger.info("✓ Test message sent successfully!")
        else:
            logger.error("✗ Failed to send test message")
    finally:
        await bot.session.close()


async def broadcast_all(delay: float = 0.05):
    """Рассылка всем пользователям"""
    await init_db()

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    try:
        # Получаем всех пользователей
        async with async_session_maker() as session:
            result = await session.execute(select(User.telegram_id))
            user_ids = [row[0] for row in result.fetchall()]

        total = len(user_ids)
        success = 0
        failed = 0

        logger.info(f"Starting broadcast to {total} users...")

        for i, user_id in enumerate(user_ids, 1):
            if await send_to_user(bot, user_id):
                success += 1
            else:
                failed += 1

            if i % 50 == 0:
                logger.info(f"Progress: {i}/{total} (success: {success}, failed: {failed})")

            if delay > 0:
                await asyncio.sleep(delay)

        logger.info(f"Broadcast completed: {success} sent, {failed} failed out of {total}")

    finally:
        await bot.session.close()


def main():
    parser = argparse.ArgumentParser(description="Broadcast referral + channel bonus message")
    parser.add_argument("--test", type=int, help="Send test message to specific user ID")
    parser.add_argument("--all", action="store_true", help="Send to all users")
    parser.add_argument("--delay", type=float, default=0.05, help="Delay between messages in seconds")

    args = parser.parse_args()

    if args.test:
        asyncio.run(broadcast_test(args.test))
    elif args.all:
        confirm = input("Are you sure you want to send to ALL users? (yes/no): ")
        if confirm.lower() == "yes":
            asyncio.run(broadcast_all(args.delay))
        else:
            print("Cancelled.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
