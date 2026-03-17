# Deployment Guide — GovDoc AI

## Option 1: Render (Recommended)

### Prerequisites
- Render account (https://render.com)
- GitHub repo connected to Render

### Steps

1. **Create a Blueprint** on Render:
   - Go to Dashboard → New → Blueprint
   - Connect this repository
   - Render reads `render.yaml` and provisions: backend, database, frontend

2. **Set environment variables** after Blueprint creates the services:
   - `ANTHROPIC_API_KEY` — your Anthropic API key (on the backend service)
   - `CORS_ORIGINS` — the frontend URL (e.g., `https://govdoc-ai-frontend.onrender.com`)

3. **Verify**:
   - Backend health: `https://govdoc-ai-backend.onrender.com/api/health`
   - Frontend: `https://govdoc-ai-frontend.onrender.com`

### How it works
- Frontend is a Render Static Site with a rewrite rule: `/api/*` → backend service
- Backend auto-connects to PostgreSQL via `DATABASE_URL` from Render
- The config auto-normalizes `postgres://` URLs to `postgresql+asyncpg://` for asyncpg

---

## Option 2: Railway

```bash
# Install CLI
npm i -g @railway/cli

# Login
railway login

# Create project
railway init

# Add PostgreSQL
railway add --plugin postgresql

# Deploy backend
cd backend
railway up

# Deploy frontend (separate service)
cd ../frontend
railway up
```

Set env vars in Railway dashboard: `ANTHROPIC_API_KEY`, `API_KEY`.

---

## Option 3: Docker Compose (local/VPS)

```bash
ANTHROPIC_API_KEY=sk-ant-... docker-compose up -d
```

Accessible at `http://localhost:3000`.
