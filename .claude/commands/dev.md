# Start Development

Start frontend dev server and backend in parallel.

Frontend:
```bash
npm run dev
```

Backend (in separate terminal):
```bash
cd backend && uvicorn app.main:app --reload --port 8000
```
