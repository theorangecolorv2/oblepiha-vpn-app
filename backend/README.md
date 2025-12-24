# Oblepiha VPN Backend

FastAPI бэкенд для Telegram Mini App VPN сервиса.

## Технологии

- **Python 3.12+**
- **FastAPI** — async web framework
- **SQLite + SQLAlchemy 2.0** — база данных
- **httpx** — async HTTP client для Remnawave API
- **YooKassa SDK** — платежи

## Структура

```
backend/
├── app/
│   ├── main.py           # FastAPI приложение
│   ├── config.py         # Настройки из .env
│   ├── database.py       # SQLite + SQLAlchemy
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── routers/          # API endpoints
│   ├── services/         # Бизнес-логика
│   └── middleware/       # Auth middleware
├── data/                 # SQLite БД (создаётся автоматически)
├── requirements.txt
├── Dockerfile
└── env.example
```

## Настройка

### 1. Создать .env файл

```bash
cp env.example .env
```

Заполнить все значения:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token

# Remnawave Panel
REMNAWAVE_API_URL=https://your-panel.com
REMNAWAVE_API_TOKEN=your_api_token

# YooKassa
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Запустить

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Тарифы
- `GET /api/tariffs` — список тарифов

### Пользователи
- `GET /api/users/me` — данные текущего пользователя
- `GET /api/users/me/stats` — статистика для главного экрана

### Платежи
- `POST /api/payments` — создать платёж
- `POST /api/payments/webhook` — webhook от YooKassa
- `GET /api/payments/history` — история платежей
- `GET /api/payments/{id}/status` — статус платежа

## Авторизация

Все запросы (кроме `/api/tariffs` и webhook) требуют заголовок:

```
X-Telegram-Init-Data: <initData from Telegram WebApp>
```

## Docker

```bash
# Сборка
docker build -t oblepiha-backend ./backend

# Запуск
docker run -d -p 8000:8000 --env-file ./backend/.env oblepiha-backend
```

## YooKassa Webhook

Для работы платежей настрой webhook в личном кабинете YooKassa:

- **URL:** `https://oblepiha-app.ru/api/payments/webhook`
- **События:** `payment.succeeded`, `payment.canceled`

## Remnawave Squad

Все пользователи автоматически добавляются в squad:
```
REMNAWAVE_SQUAD_ID=406c6e73-489d-4d38-8868-4af594bb6a86
```

Это обеспечивает изоляцию пользователей Облепиха VPN от других сервисов на той же панели.

