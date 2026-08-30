# TripPilot AI — Stage 1

Full-stack foundation for an Agentic AI Travel Assistant.

## Included

- Next.js 15 + TypeScript frontend
- FastAPI backend with JWT authentication
- PostgreSQL + SQLAlchemy + Alembic
- Register/login, protected dashboard, create trips, trip history
- Chat UI placeholder ready for the Stage 2 AI planner
- Docker Compose development environment
- Backend API tests

## Quick start with Docker

1. Copy the environment file:

   ```bash
   cp .env.example .env
   ```

2. Start everything:

   ```bash
   docker compose up --build
   ```

3. Open:

   - Web app: http://localhost:3000
   - API docs: http://localhost:8000/docs

The API container runs migrations automatically.

## Local development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## API routes

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Get JWT |
| GET | `/api/v1/auth/me` | Current user |
| GET | `/api/v1/trips` | List user's trips |
| POST | `/api/v1/trips` | Create a trip |
| GET | `/api/v1/trips/{id}` | Get one trip |
| DELETE | `/api/v1/trips/{id}` | Delete one trip |
| GET | `/health` | Health check |

## Stage 2 extension point

Replace the local response in `frontend/src/components/ChatPanel.tsx` with a call to a new `/api/v1/agent/plan` endpoint. The trip model already contains `request_text`, `itinerary`, and lifecycle status fields needed for structured AI output.

