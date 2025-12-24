"""
Pydantic схемы для платежей.
"""

from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PaymentCreate(BaseModel):
    """Создание платежа"""
    tariff_id: str


class PaymentResponse(BaseModel):
    """Ответ при создании платежа"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        by_alias=True,  # Сериализовать в camelCase
    )
    
    payment_id: str
    confirmation_url: str
    amount: int
    tariff_id: str
    tariff_name: str


class PaymentStatusResponse(BaseModel):
    """Статус платежа"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        by_alias=True,
        from_attributes=True,
    )
    
    id: int
    status: str
    tariff_id: str
    tariff_name: str
    amount: int
    days: int
    created_at: datetime
    paid_at: Optional[datetime] = None


class PaymentWebhook(BaseModel):
    """Webhook от YooKassa"""
    type: str
    event: str
    object: dict[str, Any]


class PaymentHistoryItem(BaseModel):
    """Элемент истории платежей"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        by_alias=True,
        from_attributes=True,
    )
    
    id: int
    tariff_name: str
    amount: int
    days: int
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None

