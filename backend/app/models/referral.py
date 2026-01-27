"""
Модель для отслеживания реферальных бонусов.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReferralReward(Base):
    """
    Запись о начисленном реферальном бонусе.

    Создаётся когда реферал (referred_user) покупает подписку на месяц+,
    и владелец реферальной ссылки (referrer_user) получает бонусные дни.

    UNIQUE constraint на referred_user_id гарантирует, что бонус
    за одного реферала начисляется только один раз.
    """

    __tablename__ = "referral_rewards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Кто получил бонус (владелец реферальной ссылки)
    referrer_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # За кого получен бонус (UNIQUE = бонус за реферала только 1 раз)
    referred_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    # Платёж, за который начислен бонус
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id"),
        nullable=False
    )

    # Количество бонусных дней
    bonus_days: Mapped[int] = mapped_column(Integer, default=10)

    # Когда начислен бонус
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<ReferralReward(referrer={self.referrer_user_id}, referred={self.referred_user_id}, days={self.bonus_days})>"
