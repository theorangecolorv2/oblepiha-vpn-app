"""
Модель пользователя.
Связывает Telegram ID с данными в Remnawave.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    """
    Пользователь системы.
    
    Основной ключ - telegram_id.
    Храним remnawave_uuid для связи с панелью.
    """
    
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Telegram данные
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Remnawave данные
    remnawave_uuid: Mapped[Optional[str]] = mapped_column(String(36), unique=True, nullable=True, index=True)
    remnawave_username: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    subscription_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # Статус подписки (кешируем локально)
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Реферальная система (на будущее)
    referrer_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, index=True)
    referral_code: Mapped[Optional[str]] = mapped_column(String(16), unique=True, nullable=True)
    
    # Согласие с условиями пользования
    terms_accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Пробный период
    trial_used: Mapped[bool] = mapped_column(Boolean, default=False)

    # Автопродление подписки
    auto_renew_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    payment_method_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    payment_method_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # bank_card, sbp, sber_pay, tinkoff_bank, etc.
    card_last4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    card_brand: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    sbp_phone: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # Для СБП: маскированный телефон
    last_notification_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, remnawave_uuid={self.remnawave_uuid})>"

