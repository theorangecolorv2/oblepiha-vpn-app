"""
Модуль планировщика задач.

Используется для:
- Синхронизации локальной БД с Remnawave
- Уведомлений об истечении подписки
- Автопродления подписок
"""

from app.scheduler.scheduler import setup_scheduler, shutdown_scheduler

__all__ = ["setup_scheduler", "shutdown_scheduler"]
