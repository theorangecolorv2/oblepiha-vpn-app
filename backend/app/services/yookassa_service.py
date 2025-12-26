"""
Сервис для работы с YooKassa.
"""

import logging
import uuid
from typing import Optional

from yookassa import Configuration, Payment as YKPayment
from yookassa.domain.response import PaymentResponse as YKPaymentResponse

from app.config import get_settings, get_tariff_by_id

logger = logging.getLogger(__name__)


class YooKassaService:
    """Сервис для работы с YooKassa API"""

    def __init__(self):
        settings = get_settings()
        Configuration.account_id = settings.yookassa_shop_id
        Configuration.secret_key = settings.yookassa_secret_key
        self.return_url = settings.yookassa_return_url

    def create_payment(
        self,
        tariff_id: str,
        telegram_id: int,
        user_id: int,
        save_payment_method: bool = False,
    ) -> Optional[YKPaymentResponse]:
        """
        Создать платёж в YooKassa.

        Args:
            tariff_id: ID тарифа
            telegram_id: Telegram ID пользователя
            user_id: ID пользователя в нашей БД
            save_payment_method: Сохранить способ оплаты для автоплатежей

        Returns:
            Объект платежа YooKassa или None
        """
        tariff = get_tariff_by_id(tariff_id)
        if not tariff:
            logger.error(f"Tariff not found: {tariff_id}")
            return None

        try:
            metadata = {
                "tariff_id": tariff_id,
                "telegram_id": str(telegram_id),
                "user_id": str(user_id),
                "days": str(tariff["days"]),
            }

            # Флаг для webhook что нужно включить автопродление
            if save_payment_method:
                metadata["setup_auto_renew"] = "true"

            payment_data = {
                "amount": {
                    "value": str(tariff["price"]) + ".00",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.return_url
                },
                "capture": True,
                "description": f"Облепиха VPN - {tariff['name']}",
                "metadata": metadata,
            }

            # Сохранение способа оплаты для автопродления
            if save_payment_method:
                payment_data["save_payment_method"] = True
                payment_data["merchant_customer_id"] = str(telegram_id)

            payment = YKPayment.create(payment_data, uuid.uuid4())

            logger.info(
                f"Created YooKassa payment: {payment.id} for user {telegram_id}, "
                f"tariff {tariff_id}, save_method={save_payment_method}"
            )

            return payment

        except Exception as e:
            logger.error(f"Error creating YooKassa payment: {e}")
            return None

    def create_auto_payment(
        self,
        payment_method_id: str,
        amount: int,
        telegram_id: int,
        user_id: int,
        days: int,
        description: str = "Облепиха VPN - Автопродление",
    ) -> Optional[YKPaymentResponse]:
        """
        Создать автоплатёж по сохранённому способу оплаты.

        Платёж проходит без подтверждения пользователя (безакцептное списание).
        Требует включённых рекуррентных платежей в YooKassa.

        Args:
            payment_method_id: ID сохранённого способа оплаты
            amount: Сумма в рублях
            telegram_id: Telegram ID пользователя
            user_id: ID пользователя в нашей БД
            days: Количество дней подписки
            description: Описание платежа

        Returns:
            Объект платежа YooKassa или None
        """
        try:
            payment = YKPayment.create({
                "amount": {
                    "value": str(amount) + ".00",
                    "currency": "RUB"
                },
                "capture": True,
                "payment_method_id": payment_method_id,
                "description": description,
                "metadata": {
                    "tariff_id": "month",
                    "telegram_id": str(telegram_id),
                    "user_id": str(user_id),
                    "days": str(days),
                    "is_auto_payment": "true",
                }
            }, uuid.uuid4())

            logger.info(
                f"Created auto-payment: {payment.id} for user {telegram_id}, "
                f"amount={amount}, payment_method={payment_method_id}"
            )

            return payment

        except Exception as e:
            logger.error(f"Error creating auto-payment for user {telegram_id}: {e}")
            return None

    def get_payment(self, payment_id: str) -> Optional[YKPaymentResponse]:
        """Получить информацию о платеже"""
        try:
            return YKPayment.find_one(payment_id)
        except Exception as e:
            logger.error(f"Error getting YooKassa payment {payment_id}: {e}")
            return None

    def is_payment_succeeded(self, payment: YKPaymentResponse) -> bool:
        """Проверить, успешен ли платёж"""
        return payment.status == "succeeded" and payment.paid


# Singleton instance
_yookassa_service: Optional[YooKassaService] = None


def get_yookassa_service() -> YooKassaService:
    """Получить экземпляр сервиса YooKassa"""
    global _yookassa_service
    if _yookassa_service is None:
        _yookassa_service = YooKassaService()
    return _yookassa_service

