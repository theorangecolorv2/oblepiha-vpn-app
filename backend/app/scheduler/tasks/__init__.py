"""
Задачи планировщика.
"""

from app.scheduler.tasks.sync_remnawave import sync_users_with_remnawave
from app.scheduler.tasks.expiration_notify import send_expiration_notifications
from app.scheduler.tasks.auto_renew import process_auto_renewals

__all__ = [
    "sync_users_with_remnawave",
    "send_expiration_notifications",
    "process_auto_renewals",
]
