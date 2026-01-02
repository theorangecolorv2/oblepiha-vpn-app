# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

**Oblepiha VPN Mini App** - Telegram Mini App для продажи VPN подписок.
- **Frontend**: React 19 + TypeScript + Vite + Tailwind
- **Backend**: FastAPI + SQLite + SQLAlchemy
- **Integrations**: Remnawave (VPN provider), YooKassa (payments), Telegram WebApp

## Commands

```bash
# Frontend
npm run dev          # Vite dev server (localhost:5173)
npm run build        # Build to /dist
npm run lint         # ESLint

# Backend
cd backend
uvicorn app.main:app --reload --port 8000    # Dev server
python run_bot.py                             # Telegram bot

# Docker
docker compose up -d --build    # All services
```

---

## FILE MAP: Frontend (src/)

### Entry & Routing
| File | Contents |
|------|----------|
| `main.tsx` | `Router()` - pathname routing: `/`→App, `/sub`→SubPage, `/info`→InfoPage; `hideLoader()` |
| `App.tsx` | Main component with tabs (shop/vpn/friends), payment flow, `handlePayment()`, `proceedWithPayment()`, `handleTermsAgree()` |

### Components (src/components/)
| File | Component | Purpose |
|------|-----------|---------|
| `Header.tsx` | `Header({firstName})` | Logo + greeting |
| `Stats.tsx` | `Stats({isActive, daysLeft, trafficLeftGb, ...})` | Subscription stats card (3 columns) |
| `TariffCard.tsx` | `TariffCard({tariff, isSelected, onSelect, ...})` | Tariff selection card |
| `Button.tsx` | `Button({variant, disabled, ...})` | Primary/secondary button |
| `BottomNav.tsx` | `BottomNav({activeTab, onTabChange})` | Tab navigation (shop/vpn/friends) |
| `ConnectionScreen.tsx` | `ConnectionScreen({userOS, subscriptionUrl, isActive})` | VPN setup instructions by OS |
| `TermsAgreementModal.tsx` | `TermsAgreementModal({isOpen, onAgree})` | Terms acceptance modal |
| `AutoRenewModal.tsx` | `AutoRenewModal({isOpen, isEnabled, onClose, onToggle})` | Auto-renewal settings |
| `ReferralScreen.tsx` | `ReferralScreen()` | Placeholder "coming soon" |

### Pages (src/pages/)
| File | Component | Purpose |
|------|-----------|---------|
| `SubPage.tsx` | `SubPage()` | Auto-redirect to Happ via deep link (`happ://add/{url}`) |
| `InfoPage.tsx` | `InfoPage()` | FAQ + Terms accordion |

### Hooks (src/hooks/)
| File | Hook | Returns |
|------|------|---------|
| `useTelegram.ts` | `useTelegram()` | `{tg, isReady, firstName, user, userOS}` - Telegram WebApp init |
| `useUser.ts` | `useUser()` | `{isLoading, stats, tariffs, user, refreshStats(), createPayment(), acceptTerms(), refreshUser()}` |

### API & Config (src/)
| File | Contents |
|------|----------|
| `api/index.ts` | `apiFetch()`, `api.getTariffs()`, `api.getCurrentUser()`, `api.getUserStats()`, `api.createPayment()`, `api.getPaymentStatus()`, `api.acceptTerms()` |
| `config.ts` | `config` object: apiUrl, supportTg, termsUrl, happDownload, v2rayDownload, happDeepLink |
| `constants.ts` | `STRINGS` (Russian localization), `UNITS` |
| `types.ts` | `Tariff`, `UserData`, `VpnStatus` interfaces |
| `data/tariffs.ts` | Fallback tariffs array for dev |

---

## FILE MAP: Backend (backend/app/)

### Main Application
| File | Contents |
|------|----------|
| `main.py` | FastAPI app, CORS config, router includes, `/health` endpoint |
| `config.py` | `Settings` class (env vars), `TARIFFS` array, `get_tariff_by_id()` |
| `database.py` | `Base`, `engine`, `async_session_maker`, `init_db()`, `get_db()` |

### Models (backend/app/models/)
| File | Model | Key Fields |
|------|-------|------------|
| `user.py` | `User` | telegram_id, remnawave_uuid, subscription_url, subscription_expires_at, is_active, auto_renew_enabled, payment_method_id, trial_used, terms_accepted_at |
| `payment.py` | `Payment` | user_id, tariff_id, amount, yookassa_payment_id, status, payment_method_id, is_auto_payment |

### Schemas (backend/app/schemas/)
| File | Classes |
|------|---------|
| `user.py` | `UserFromTelegram`, `UserCreate`, `UserResponse`, `UserStatsResponse` |
| `payment.py` | `PaymentCreate`, `PaymentResponse`, `PaymentStatusResponse`, `PaymentWebhook`, `PaymentHistoryItem` |
| `tariff.py` | `TariffResponse` |

### Routers (backend/app/routers/)
| File | Prefix | Endpoints |
|------|--------|-----------|
| `users.py` | `/api/users` | `GET /me`, `GET /me/stats`, `POST /me/accept-terms`, `GET /me/auto-renew/status`, `POST /me/auto-renew/enable`, `POST /me/auto-renew/disable`, `DELETE /me/auto-renew/payment-method` |
| `payments.py` | `/api/payments` | `POST /` (create), `POST /webhook`, `GET /history`, `GET /{id}/status` |
| `tariffs.py` | `/api/tariffs` | `GET /`, `GET /{id}` |

### Services (backend/app/services/)
| File | Class/Functions | Purpose |
|------|-----------------|---------|
| `remnawave.py` | `RemnawaveService` | `get_user_by_telegram_id()`, `get_user_by_username()`, `get_user_by_uuid()`, `create_user()`, `update_user_expiration()` |
| `yookassa_service.py` | `YooKassaService` | `create_payment()`, `create_auto_payment()`, `get_payment()`, `is_payment_succeeded()` |
| `telegram.py` | Functions | `validate_init_data()`, `parse_user_from_init_data()` |
| `telegram_notify.py` | Functions | `send_payment_success_message()`, `send_expiration_warning()`, `send_auto_renew_success()`, `send_auto_renew_failed()`, `send_subscription_expired()` |

### Middleware (backend/app/middleware/)
| File | Contents |
|------|----------|
| `auth.py` | `TelegramUser`, `get_current_user()` - validates X-Telegram-Init-Data header |

### Scheduler (backend/app/scheduler/)
| File | Contents |
|------|----------|
| `scheduler.py` | `setup_scheduler()`, APScheduler config |
| `tasks/auto_renew.py` | `process_auto_renewals()` - runs every hour at :30 |
| `tasks/expiration_notify.py` | `send_expiration_notifications()` - runs every hour at :00 |
| `tasks/sync_remnawave.py` | `sync_users_with_remnawave()` - runs every 6 hours |

### Bot (backend/app/bot/)
| File | Contents |
|------|----------|
| `bot.py` | Telegram bot initialization |
| `handlers.py` | Bot command handlers |

---

## QUICK REFERENCE: Where to Find

### Frontend
| Need to... | Go to |
|------------|-------|
| Change routing | `src/main.tsx` |
| Modify main app logic | `src/App.tsx` |
| Edit UI component | `src/components/{Name}.tsx` |
| Change API calls | `src/api/index.ts` |
| Update user state logic | `src/hooks/useUser.ts` |
| Modify Telegram integration | `src/hooks/useTelegram.ts` |
| Change app config (URLs, links) | `src/config.ts` |
| Edit text/localization | `src/constants.ts` |
| Add/modify types | `src/types.ts` |

### Backend
| Need to... | Go to |
|------------|-------|
| Add API endpoint | `backend/app/routers/{resource}.py` |
| Modify DB model | `backend/app/models/{model}.py` |
| Change API schemas | `backend/app/schemas/{schema}.py` |
| Edit Remnawave integration | `backend/app/services/remnawave.py` |
| Edit YooKassa integration | `backend/app/services/yookassa_service.py` |
| Modify auth logic | `backend/app/middleware/auth.py` |
| Edit Telegram validation | `backend/app/services/telegram.py` |
| Change notifications | `backend/app/services/telegram_notify.py` |
| Modify scheduled tasks | `backend/app/scheduler/tasks/*.py` |
| Edit tariffs | `backend/app/config.py` → `TARIFFS` |
| Change env config | `backend/app/config.py` → `Settings` |

---

## KEY FLOWS

### Payment Flow
```
User clicks "Pay" in App.tsx
  → handlePayment() checks terms_accepted_at
  → shows TermsAgreementModal if needed
  → proceedWithPayment() calls useUser.createPayment(tariffId)
  → api.createPayment() → POST /api/payments
  → backend creates YooKassa payment
  → returns confirmation_url
  → frontend opens URL (tg.openLink)
  → YooKassa webhook → POST /api/payments/webhook
  → backend extends subscription in Remnawave
  → sends Telegram notification
```

### Auto-Renewal Flow
```
Scheduler runs process_auto_renewals() every hour at :30
  → finds users with: auto_renew_enabled=true, payment_method_id exists, subscription expires within ±1 hour
  → creates auto-payment via YooKassa (no user confirmation)
  → on success: extends Remnawave subscription, sends notification
  → on failure: sends error notification, schedules retry
```

### User Auth Flow
```
Frontend sends X-Telegram-Init-Data header with every request
  → middleware/auth.py validates signature via telegram.py
  → parses user data from initData
  → creates user in DB if not exists
  → creates Remnawave user if needed
  → returns TelegramUser to endpoint
```

---

## RULES FOR CLAUDE

1. **Never search for files blindly** - use the file maps above
2. **Check Quick Reference first** when asked to modify something
3. **Frontend state lives in hooks** - useUser for user data, useTelegram for Telegram
4. **Backend uses dependency injection** - get_current_user, get_db
5. **All money amounts in backend are in kopecks** (1 ruble = 100 kopecks)
6. **Tariffs are defined in backend/app/config.py TARIFFS** - single source of truth
7. **User identification**: Remnawave username format is `oblepiha_{telegram_id}` or `oblepiha_{telegram_id}_{tg_username}`
8. **API auth**: All endpoints except `/api/tariffs` and `/api/payments/webhook` require auth
9. **Localization**: All Russian strings are in `src/constants.ts`
10. **Deep links**: Happ app uses `happ://add/{subscription_url}` scheme

---

## ENVIRONMENT VARIABLES

Backend requires these in `.env`:
```
TELEGRAM_BOT_TOKEN=        # Telegram bot token
REMNAWAVE_API_URL=         # Remnawave API base URL
REMNAWAVE_API_TOKEN=       # Remnawave bearer token
REMNAWAVE_SQUAD_ID=        # Internal squad ID
REMNAWAVE_EXTERNAL_SQUAD_ID=  # External squad ID for links
YOOKASSA_SHOP_ID=          # YooKassa shop ID
YOOKASSA_SECRET_KEY=       # YooKassa secret key
YOOKASSA_RETURN_URL=       # Return URL after payment
FRONTEND_URL=              # Frontend URL for CORS
```

Frontend uses:
```
VITE_API_URL=              # Backend API URL (defaults to localhost:8000)
```
