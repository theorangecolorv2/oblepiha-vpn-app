from app.routers.users import router as users_router
from app.routers.payments import router as payments_router
from app.routers.tariffs import router as tariffs_router

__all__ = ["users_router", "payments_router", "tariffs_router"]

