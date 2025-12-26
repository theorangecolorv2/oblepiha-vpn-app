# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Oblepiha VPN Mini App - A Telegram Mini App for selling VPN subscriptions. React frontend communicates with a FastAPI backend that integrates with Remnawave VPN provider and YooKassa payment processing.

## Commands

### Frontend
```bash
npm run dev      # Start Vite dev server
npm run build    # TypeScript compile + Vite build (outputs to /dist)
npm run lint     # ESLint on TypeScript files
npm run preview  # Preview production build
```

### Backend
```bash
cd backend
python run_bot.py                              # Run Telegram bot
uvicorn app.main:app --reload --port 8000      # Development server
uvicorn app.main:app --host 0.0.0.0 --port 8000  # Production
```

### Docker
```bash
docker compose up -d --build  # Build and run all services
```
Services: `oblepiha-frontend` (nginx:3000), `oblepiha-backend` (FastAPI:8000), `oblepiha-bot`

## Architecture

### Frontend (React 19 + TypeScript + Vite + Tailwind)
- **Routing**: Simple pathname-based routing in `main.tsx` (`/` → App, `/sub` → SubPage, `/info` → InfoPage)
- **Telegram Integration**: `useTelegram` hook handles WebApp SDK, OS detection, haptic feedback
- **Auth**: `X-Telegram-Init-Data` header sent with all API requests via `api/index.ts`
- **State**: `useUser` hook manages user data, stats, payment flow
- **Main tabs**: Shop (buy subscriptions), VPN (setup instructions), Friends (referrals - coming soon)

### Backend (FastAPI + SQLite + SQLAlchemy)
- **Auth Middleware** (`middleware/auth.py`): Validates Telegram initData, auto-creates users
- **Routers**: `tariffs.py`, `users.py`, `payments.py` - standard REST endpoints
- **Services**:
  - `remnawave.py` - VPN provider API (create/extend subscriptions)
  - `yookassa_service.py` - Payment creation and processing
  - `telegram.py` - initData validation
  - `telegram_notify.py` - Bot notifications to users
- **Database**: SQLite with Alembic migrations, models in `models/`

### API Endpoints
- `GET /api/tariffs` - Public
- `GET /api/users/me` - User info (auth required)
- `GET /api/users/me/stats` - Subscription stats (auth required)
- `POST /api/users/me/accept-terms` - Accept ToS (auth required)
- `POST /api/payments` - Create payment (auth required)
- `POST /api/payments/webhook` - YooKassa callback (no auth, IP validation)
- `GET /api/payments/{id}/status` - Check payment (auth required)

## Key Files

- `src/config.ts` - Frontend configuration (API URL, deep link schemes)
- `src/constants.ts` - Localized strings (Russian)
- `backend/app/config.py` - Backend settings from environment
- `backend/env.example` - Required environment variables

## Payment Flow

1. User selects tariff in TariffCard
2. TermsAgreementModal shown if not yet accepted
3. POST /api/payments creates YooKassa payment
4. User redirected to payment URL
5. Webhook at /api/payments/webhook processes result
6. Backend calls Remnawave API to create/extend subscription
