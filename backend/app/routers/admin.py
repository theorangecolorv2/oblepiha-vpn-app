"""
Роутер для админ-панели.
Все эндпоинты требуют проверки админского доступа.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.config import ADMIN_IDS
from app.middleware.auth import TelegramUser, get_current_user


router = APIRouter(prefix="/api/admin", tags=["admin"])


async def require_admin(user: TelegramUser = Depends(get_current_user)) -> TelegramUser:
    """Dependency для проверки админского доступа"""
    if user.id not in ADMIN_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


class AdminMeResponse(BaseModel):
    """Ответ на /admin/me"""
    id: int
    first_name: str
    is_admin: bool = True


@router.get("/me", response_model=AdminMeResponse)
async def admin_me(admin: TelegramUser = Depends(require_admin)):
    """Проверка админского доступа и получение информации о текущем админе"""
    return AdminMeResponse(
        id=admin.id,
        first_name=admin.first_name or "Admin"
    )
