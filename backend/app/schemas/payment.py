"""
Pydantic схемы для платежей.
"""

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class PaymentCreate(BaseModel):
    """Создание платежа"""
    tariff_id: str


class PaymentResponse(BaseModel):
    """Ответ при создании платежа"""
    payment_id: str
    confirmation_url: str
    amount: int
    tariff_id: str
    tariff_name: str


class PaymentStatusResponse(BaseModel):
    """Статус платежа"""
    id: int
    status: str
    tariff_id: str
    tariff_name: str
    amount: int
    days: int
    created_at: datetime
    paid_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }


class PaymentWebhook(BaseModel):
    """Webhook от YooKassa"""
    type: str
    event: str
    object: dict[str, Any]


class PaymentHistoryItem(BaseModel):
    """Элемент истории платежей"""
    id: int
    tariff_name: str
    amount: int
    days: int
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }

