"""
Модель платежа.
История всех транзакций пользователей.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Payment(Base):
    """
    История платежей.
    
    Храним все транзакции для аналитики и поддержки.
    """
    
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Связь с пользователем
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    
    # Данные тарифа
    tariff_id: Mapped[str] = mapped_column(String(32), nullable=False)
    tariff_name: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # В копейках/центах
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # YooKassa данные
    yookassa_payment_id: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True, index=True)
    payment_method_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Статус: pending, waiting_for_capture, succeeded, canceled
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)

    # Автоплатёж
    is_auto_payment: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_payment_attempt: Mapped[int] = mapped_column(Integer, default=0)
    
    # Дополнительные данные (JSON строка)
    metadata_json: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, user_id={self.user_id}, status={self.status}, amount={self.amount})>"

