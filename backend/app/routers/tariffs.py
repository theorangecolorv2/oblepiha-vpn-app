"""
API для тарифов.
Единый источник правды для фронтенда.
"""

from fastapi import APIRouter

from app.config import TARIFFS
from app.schemas.tariff import TariffResponse

router = APIRouter(prefix="/api/tariffs", tags=["tariffs"])


@router.get("", response_model=list[TariffResponse])
async def get_tariffs():
    """Получить список всех тарифов"""
    return TARIFFS


@router.get("/{tariff_id}", response_model=TariffResponse)
async def get_tariff(tariff_id: str):
    """Получить тариф по ID"""
    for tariff in TARIFFS:
        if tariff["id"] == tariff_id:
            return tariff
    
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Tariff not found")

