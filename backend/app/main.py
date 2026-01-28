"""
Oblepiha VPN Backend
FastAPI приложение для Telegram Mini App
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import users_router, payments_router, tariffs_router
from app.routers.admin import router as admin_router

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG if get_settings().debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Приглушаем шумные логгеры
logging.getLogger("httpx").setLevel(logging.WARNING)  # Отключаем логи каждого HTTP запроса
logging.getLogger("httpcore").setLevel(logging.WARNING)


class AccessLogFilter(logging.Filter):
    """
    Фильтр для uvicorn access log - пропускает только важные запросы.
    Фильтрует частые рутинные запросы типа /api/users/me/stats.
    """
    # Эндпоинты которые не логируем при успешном ответе (200)
    QUIET_ENDPOINTS = {
        "/api/users/me/stats",
        "/api/users/me",
        "/api/tariffs",
        "/health",
        "/api/ping",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        # Всегда логируем ошибки и предупреждения
        if record.levelno >= logging.WARNING:
            return True

        # Парсим сообщение uvicorn access log
        # Формат: "IP:PORT - "METHOD /path HTTP/1.1" STATUS"
        message = record.getMessage()

        # Если это успешный запрос (200, 304) на тихий эндпоинт - не логируем
        for endpoint in self.QUIET_ENDPOINTS:
            if endpoint in message and (" 200 " in message or " 304 " in message):
                return False

        return True


# Применяем фильтр к uvicorn access логгеру
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.addFilter(AccessLogFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hooks"""
    # Startup
    logger.info("Starting Oblepiha VPN Backend...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Создаём приложение
app = FastAPI(
    title="Oblepiha VPN API",
    description="Backend API для Telegram Mini App VPN сервиса",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - разрешаем запросы с фронтенда
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "https://oblepiha-app.ru",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(users_router)
app.include_router(payments_router)
app.include_router(tariffs_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    """Health check"""
    return {"status": "ok", "service": "Oblepiha VPN API"}


@app.get("/health")
async def health():
    """Health check для мониторинга"""
    return {"status": "healthy"}


@app.get("/api/ping")
async def ping():
    """Простой ping для проверки связи frontend → backend через Caddy"""
    return {"pong": True, "service": "oblepiha-backend"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

