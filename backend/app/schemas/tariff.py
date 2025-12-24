"""
Pydantic схемы для тарифов.
"""

from typing import Literal

from pydantic import BaseModel


class TariffResponse(BaseModel):
    """Тариф"""
    id: str
    name: str
    description: str
    price: int
    days: int
    icon: Literal["trial", "month", "quarter"]

