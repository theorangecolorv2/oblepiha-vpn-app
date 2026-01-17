# Start Development

Start local development servers for frontend and backend.

## Prerequisites:
- Node.js 18+
- Python 3.11+
- Backend `.env` file configured (copy from `backend/env.example`)

## Start frontend:
```bash
npm run dev
```
Frontend runs at http://localhost:5173

## Start backend (separate terminal):
```bash
cd backend && uvicorn app.main:app --reload --port 8000
```
Backend runs at http://localhost:8000
API docs at http://localhost:8000/docs

## Environment setup:

Frontend uses mock data in dev mode (no Telegram WebApp).
See `src/config.ts` for `devMode` and `mockUserData`.

Backend requires `.env` with:
- TELEGRAM_BOT_TOKEN
- REMNAWAVE_* credentials
- YOOKASSA_* credentials

## Testing Telegram Mini App locally:

Use ngrok or similar to expose localhost:
```bash
ngrok http 5173
```
Then set the ngrok URL in BotFather for your test bot.

## Remember:
- All code changes deploy via CI/CD after push to main
- Test thoroughly before pushing
- Run `/check` before committing
