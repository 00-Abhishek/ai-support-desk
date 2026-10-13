# AI-Powered Support Desk

A full-stack support-ticket application: customers/requesters raise tickets, support
agents triage them (assign, prioritise, move through a controlled workflow), and an
**optional** AI helper suggests a category, priority and draft reply — which a human
must review before it is applied.

> This is a demonstration project. AI suggestions are proposals only; the persisted
> ticket data is always under application/user control.

## Features

- Sign-in with JWT auth and role-aware access (`requester`, `agent`, `admin`).
- Create a ticket with title, description, category and priority.
- Ticket list with search, status/priority filters and bounded pagination.
- Ticket detail page: status, assignee, comments and a full activity timeline.
- Enforced workflow: `Open → In Progress → Waiting → Resolved → Closed` with
  validated transitions (illegal jumps are rejected with `422`).
- Assign an agent and set priority (`Low`, `Medium`, `High`, `Urgent`).
- Dashboard counts for open / in-progress / waiting / resolved / closed.
- Optional AI action that proposes category, priority, rationale and a draft reply.

## Architecture

```
React (Vite)  ──fetch/JSON──▶  FastAPI routes
                                  ├─ auth & authorization (JWT)
                                  ├─ Pydantic validation
                                  ├─ ticket service (workflow rules)
                                  └─ optional AI service (stub or provider)
                                        │
                                        ▼
                              SQLAlchemy  ──▶  PostgreSQL
```

Route handlers stay thin; business rules (valid status transitions, assignment
rules) live in `app/services/` and are covered by tests. The AI service is a
separate module, so the ticket workflow keeps working if AI is disabled or the
provider is unavailable.

## Tech stack

| Layer     | Technology                                   |
|-----------|----------------------------------------------|
| Frontend  | React 18, Vite, React Router, plain CSS      |
| Backend   | FastAPI, Pydantic v2, SQLAlchemy 2, PyJWT    |
| Database  | PostgreSQL 16                                |
| Tests     | pytest, FastAPI TestClient                   |
| Packaging | Docker, docker-compose                       |

## Prerequisites

- Node.js 20 LTS and npm
- Python 3.11+
- PostgreSQL 16 (or Docker)
- Git

```bash
node --version && npm --version && python --version && git --version
```

## Quick start with Docker

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

The backend creates its schema and seeds demo data on first start.

## Manual local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Point at your local PostgreSQL
export DATABASE_URL="postgresql+psycopg://support:support@localhost:5432/support_desk"
export SECRET_KEY="dev-secret-change-me"

uvicorn app.main:app --reload --port 8000
```

Tables are created automatically on startup and demo users/tickets are seeded.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # sets VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

## Demo accounts

| Email                     | Password    | Role      |
|---------------------------|-------------|-----------|
| admin@example.com         | admin123    | admin     |
| agent@example.com         | agent123    | agent     |
| requester@example.com     | request123  | requester |

## Environment variables

| Variable          | Purpose                                             | Default |
|-------------------|-----------------------------------------------------|---------|
| `DATABASE_URL`    | SQLAlchemy database URL                             | postgres |
| `SECRET_KEY`      | JWT signing key — set a strong value in production  | dev value |
| `CORS_ORIGINS`    | Comma-separated allowed frontend origins            | http://localhost:5173 |
| `AI_ENABLED`      | Turn the AI suggestion endpoint on/off              | true |
| `AI_PROVIDER`     | `stub` (offline) or a real provider                 | stub |
| `AI_MODEL`        | Model name recorded with suggestions                | stub-heuristic-v1 |
| `OPENAI_API_KEY`  | Only needed for a real provider                     | empty |

Only `.env.example` is committed. Never commit real secrets.

## API overview

| Method | Path                          | Notes                        |
|--------|-------------------------------|------------------------------|
| POST   | `/api/auth/register`          | Create a user                |
| POST   | `/api/auth/token`             | Login (OAuth2 password form) |
| GET    | `/api/auth/me`                | Current user                 |
| POST   | `/api/tickets`                | Create ticket                |
| GET    | `/api/tickets`                | List + filter + paginate     |
| GET    | `/api/tickets/{id}`           | Detail with comments/events  |
| PATCH  | `/api/tickets/{id}`           | Update status/priority/assignee (agent/admin) |
| POST   | `/api/tickets/{id}/comments`  | Add comment                  |
| POST   | `/api/tickets/{id}/ai-suggest`| AI proposal (agent/admin)    |
| GET    | `/api/dashboard/summary`      | Status counts                |

Example:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token \
  -d "username=agent@example.com&password=agent123" | jq -r .access_token)

curl -s http://localhost:8000/api/tickets -H "Authorization: Bearer $TOKEN"
```

## Tests

```bash
cd backend
pytest -q
```

The suite covers auth, ticket creation, validation, workflow-transition enforcement,
role-based authorization, comments, AI suggestions and dashboard counts. Tests run
against an in-memory SQLite database, so no PostgreSQL is needed to run them.

## Project structure

```
ai-support-desk/
  frontend/          React + Vite SPA
  backend/
    app/
      api/           routers + dependencies
      core/          settings + security
      db/            session, base, seed
      models/        SQLAlchemy models
      schemas/       Pydantic schemas
      services/      ticket rules + AI service
    tests/
  docker-compose.yml
  .env.example
```

## Security notes

- Passwords are hashed with bcrypt; tokens are signed JWTs.
- Authorization is enforced on the backend (hiding a button in React is not auth).
- Input is validated server-side even though the frontend validates too.
- Ticket text is treated as untrusted input; it is never used to invoke tools.

## Known limitations & next steps

- Schema is created with SQLAlchemy `create_all` for the MVP; Alembic migrations are
  the natural next step.
- The AI provider ships as a deterministic offline stub; wiring a real model is a
  one-module change.
- Next: SLA tracking, notifications, richer analytics, and monitoring.

## Attribution

Built as a learning/demonstration project. Built with FastAPI, React, Vite and
PostgreSQL — see the official docs of each for version-specific guidance.
