"""
Инициализация и запуск Telegram бота
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config import get_settings
from app.bot.handlers import router

logger = logging.getLogger(__name__)


async def start_bot():
    """Запуск бота"""
    settings = get_settings()
    
    # Инициализация бота
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Диспетчер
    dp = Dispatcher()
    dp.include_router(router)
    
    # Информация о боте
    bot_info = await bot.get_me()
    logger.info(f"🤖 Starting bot: @{bot_info.username}")
    
    # Запуск polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def run_bot():
    """Запуск бота (точка входа)"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    asyncio.run(start_bot())


if __name__ == "__main__":
    run_bot()

