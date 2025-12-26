"""
Инициализация и настройка APScheduler.

Расписание задач:
- Синхронизация с Remnawave: каждые 6 часов (00:00, 06:00, 12:00, 18:00)
- Уведомления об истечении: каждый час в :00
- Автопродления: каждый час в :30
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.scheduler.tasks.sync_remnawave import sync_users_with_remnawave
from app.scheduler.tasks.expiration_notify import send_expiration_notifications
from app.scheduler.tasks.auto_renew import process_auto_renewals

logger = logging.getLogger(__name__)

# Глобальный экземпляр scheduler
_scheduler: AsyncIOScheduler = None


def setup_scheduler(scheduler: AsyncIOScheduler) -> None:
    """
    Настроить задачи scheduler.

    Args:
        scheduler: Экземпляр AsyncIOScheduler
    """
    global _scheduler
    _scheduler = scheduler

    # Синхронизация с Remnawave - каждые 6 часов
    scheduler.add_job(
        sync_users_with_remnawave,
        trigger=CronTrigger(hour="0,6,12,18", minute=0),
        id="sync_remnawave",
        name="Sync with Remnawave",
        replace_existing=True,
        max_instances=1,
    )

    # Уведомления об истечении - каждый час в :00
    scheduler.add_job(
        send_expiration_notifications,
        trigger=CronTrigger(minute=0),
        id="expiration_notify",
        name="Send expiration notifications",
        replace_existing=True,
        max_instances=1,
    )

    # Автопродления - каждый час в :30
    scheduler.add_job(
        process_auto_renewals,
        trigger=CronTrigger(minute=30),
        id="auto_renew",
        name="Process auto-renewals",
        replace_existing=True,
        max_instances=1,
    )

    logger.info("Scheduler jobs configured:")
    logger.info("  - sync_remnawave: every 6 hours at :00")
    logger.info("  - expiration_notify: every hour at :00")
    logger.info("  - auto_renew: every hour at :30")


def shutdown_scheduler() -> None:
    """Корректно остановить scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("Scheduler shut down gracefully")


def get_scheduler() -> AsyncIOScheduler:
    """Получить экземпляр scheduler."""
    return _scheduler
