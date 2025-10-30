# CRM Backend (FastAPI)

A lightweight CRM backend built with FastAPI, SQLAlchemy 2.x (async), Alembic, and PostgreSQL. It provides authentication, user management, contacts, leads, and tasks with fuzzy search and email flows for verification and password reset.

### Features
- Authentication with JWT (email verification, password reset)
- Role-based access control (admin, manager, user)
- CRUD for Contacts, Leads, and Tasks
- Fuzzy search using PostgreSQL pg_trgm
- Async SQLAlchemy and sessions
- Alembic migrations
- CORS and Trusted Hosts configured

## Tech Stack
- FastAPI, Starlette
- SQLAlchemy 2.x (async) + Alembic
- PostgreSQL
- python-jose, passlib[bcrypt]
- pydantic v2, pydantic-settings
- aiosmtplib (email sending)

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 13+

Enable the required PostgreSQL extension (for fuzzy search):
sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;


### Clone and navigate
bash
git clone <your-repo-url>
cd crm-project/crm-project/backend


### Create and activate a virtual environment
bash
python -m venv venv
venv\Scripts\activate  # Windows PowerShell
# source venv/bin/activate  # macOS/Linux


### Install dependencies
bash
pip install -r requirements.txt


### Environment variables (.env)
Create a .env file in backend/ with:
env
# App
ENVIRONMENT=development

# Database (async URL)
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:<port>/<db_name>

# Security
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@example.com
SMTP_PASS=your_app_password


Note: Alembic may also read alembic.ini but env.py uses settings.DATABASE_URL from .env.

## Database Setup

Run migrations (recommended):
bash
alembic upgrade head


Or create tables directly (dev only):
bash
python -m app.core.init_db


## Run the Server
From backend/:
bash
uvicorn app.api.v1.routes:router --help > NUL 2>&1  # warms imports (optional)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


- Swagger UI: http://localhost:8000/docs (disabled if ENVIRONMENT=production)
- ReDoc: http://localhost:8000/redoc
- Health: GET / → { status: "healthy" }

## API Overview

Base URL: http://localhost:8000

- Health
  - GET / health check

- Auth (/auth)
  - GET /auth/verify-email?token=...
  - POST /auth/forgot_password (body: email)
  - POST /auth/reset-password (body: token, new_password)

- General (/api/v1/general)
  - See router in app/api/v1/routes.py for user self-service endpoints below

- Users (self-service in General router)
  - POST /api/v1/general/register
  - POST /api/v1/general/login → { access_token, token_type }
  - GET /api/v1/general/me
  - PATCH /api/v1/general/me
  - DELETE /api/v1/general/me

- Admin Users (/api/v1/admin/users) [admin role required]
  - GET /api/v1/admin/users?skip=&limit=&role=&sort_by=&sort_order=&q= → paginated
  - GET /api/v1/admin/users/{user_id}
  - PATCH /api/v1/admin/users/{user_id}
  - DELETE /api/v1/admin/users/{user_id}

- Contacts (/api/v1/contacts) [auth required]
  - POST /api/v1/contacts
  - GET /api/v1/contacts?skip=&limit=&sort_by=&sort_order=&status=&source=&start_date=&end_date=&q= → paginated, fuzzy when q
  - PUT /api/v1/contacts/{contact_id}
  - DELETE /api/v1/contacts/{contact_id}

- Leads (/api/v1/leads) [auth required]
  - POST /api/v1/leads
  - GET /api/v1/leads?skip=&limit=&sort_by=&sort_order=&status=&source=&created_after=&created_before=&q= → paginated, fuzzy when q
  - GET /api/v1/leads/search?name=&status=&source=&skip=&limit=
  - PUT /api/v1/leads/{lead_id}
  - DELETE /api/v1/leads/{lead_id}

- Tasks (/api/v1/tasks) [auth required]
  - POST /api/v1/tasks
  - (Additional list/update/delete can be extended similarly)

### Auth Details
- JWT token creation: app.core.security.create_access_token
- Bearer auth via OAuth2PasswordBearer; use Authorization: Bearer <token>
- Roles check helper: require_roles(["admin"])

## CORS and Hosts
Configured in app/main.py and app/core/config.py:
- Allowed origins: common dev ports (3000, 5173, 4200, etc.)
- Docs are disabled in production (ENVIRONMENT=production)

## Email Flows (dev)
- Verification link: GET /auth/verify-email?token=...
- Reset link: POST /auth/forgot_password then POST /auth/reset-password
- SMTP via aiosmtplib; ensure SMTP_USER/SMTP_PASS are set

## Migrations Cheatsheet
bash
# Create new revision (autogenerate)
alembic revision -m "message" --autogenerate

# Upgrade / Downgrade
alembic upgrade head
alembic downgrade -1


## Running with Docker (skeleton)
A Dockerfile exists but is currently empty. You can add a production-ready image like:
Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


## Project Structure (backend)

backend/
  app/
    api/v1/            # routers (auth, admin users, contacts, leads, tasks)
    core/              # config, db, deps, security
    models/            # SQLAlchemy models
    schemas/           # Pydantic schemas
    services/          # business logic
    utils/             # email
    main.py            # FastAPI app factory
  alembic/             # migrations
  requirements.txt


## Notes
- Ensure your DATABASE_URL uses async driver: postgresql+asyncpg://...
- For fuzzy search, the pg_trgm extension must be enabled in your DB.
- Swagger docs are available in non-production.