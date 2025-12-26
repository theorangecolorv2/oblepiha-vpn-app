"""
Инициализация и запуск Telegram бота с планировщиком задач.
"""

import asyncio
import logging
import signal
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings
from app.bot.handlers import router
from app.database import init_db
from app.scheduler import setup_scheduler, shutdown_scheduler

logger = logging.getLogger(__name__)

# Глобальный scheduler для graceful shutdown
_scheduler: Optional[AsyncIOScheduler] = None


async def start_bot():
    """Запуск бота с планировщиком задач"""
    global _scheduler

    settings = get_settings()

    # Инициализация БД (нужна для scheduler)
    await init_db()
    logger.info("Database initialized")

    # Инициализация бота
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Диспетчер
    dp = Dispatcher()
    dp.include_router(router)

    # Инициализация планировщика
    _scheduler = AsyncIOScheduler()
    setup_scheduler(_scheduler)
    _scheduler.start()
    logger.info("Scheduler started")

    # Информация о боте
    bot_info = await bot.get_me()
    logger.info(f"Starting bot: @{bot_info.username}")

    # Запуск polling
    try:
        await dp.start_polling(bot)
    finally:
        # Graceful shutdown
        logger.info("Shutting down...")
        shutdown_scheduler()
        await bot.session.close()
        logger.info("Bot stopped")


def handle_shutdown(signum, frame):
    """Обработчик сигналов завершения"""
    logger.info(f"Received signal {signum}, shutting down...")
    shutdown_scheduler()


def run_bot():
    """Запуск бота (точка входа)"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Регистрируем обработчики сигналов для graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    asyncio.run(start_bot())


if __name__ == "__main__":
    run_bot()

