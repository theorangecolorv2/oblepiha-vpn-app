# Check Code Quality

Run linting, type checking, and build for both frontend and backend.

## Frontend checks:
```bash
npm run lint && npm run build
```

## Backend checks:
```bash
cd backend && python -m py_compile app/main.py app/config.py app/database.py
```

## What this checks:
- ESLint for code style and potential errors
- TypeScript compilation (via Vite build)
- Python syntax validation

## Run before pushing!
Always run `/check` before pushing to main - CI/CD will deploy automatically.
