# TaskPilot — Usage Guide

> Complete reference for installing, configuring, and using TaskPilot.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation & Setup](#installation--setup)
3. [Environment Configuration](#environment-configuration)
4. [Starting the Development Servers](#starting-the-development-servers)
5. [Authentication Flow](#authentication-flow)
6. [Using the API](#using-the-api)
7. [Using the Web UI](#using-the-web-ui)
8. [Database Setup and Migrations](#database-setup-and-migrations)

---

## System Requirements

| Component        | Minimum Version | Notes                                       |
| ---------------- | --------------- | ------------------------------------------- |
| **Python**       | 3.12+           | Backend runtime                             |
| **Node.js**      | 20+             | Frontend build & runtime                    |
| **npm**          | 10+             | Ships with Node.js 20                       |
| **PostgreSQL**   | 15+             | Production database (SQLite for local dev)  |
| **Redis**        | 7+              | Caching and queues (optional for local dev) |
| **Git**          | 2.40+           | Source control                              |
| **OS**           | macOS / Linux   | Windows via WSL2 is also supported          |

### Optional

| Tool            | Purpose                              |
| --------------- | ------------------------------------ |
| Docker 24+      | Containerised deployment             |
| Docker Compose  | Multi-service local stack            |
| Wrangler CLI    | Cloudflare Pages deployment          |
| Stripe CLI      | Local webhook testing                |

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-org>/TaskPilot.git
cd TaskPilot
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

Verify the installation:

```bash
python -c "import fastapi; print(fastapi.__version__)"
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm ci

# Verify
npx next --version
```

### 4. Create the `.env` File

```bash
# From the project root
cp ENV_Example.env backend/.env
```

Edit `backend/.env` and fill in real values (see [Environment Configuration](#environment-configuration) below).

---

## Environment Configuration

TaskPilot reads configuration from a `.env` file placed in the `backend/` directory. The full list of variables is documented in `ENV_Example.env` at the project root.

### Core

| Variable     | Description                       | Example                            |
| ------------ | --------------------------------- | ---------------------------------- |
| `NODE_ENV`   | Runtime environment               | `development` or `production`      |
| `APP_URL`    | URL where the frontend is served  | `http://localhost:3000`            |
| `API_URL`    | URL where the backend is served   | `http://localhost:8000`            |

### Database

| Variable       | Description                       | Example                                             |
| -------------- | --------------------------------- | --------------------------------------------------- |
| `DATABASE_URL` | SQLAlchemy connection string      | `postgresql://user:pass@localhost:5432/taskpilot`    |
| `REDIS_URL`    | Redis connection string           | `redis://localhost:6379/0`                           |

For **local development** you can omit `DATABASE_URL` and TaskPilot will fall back to SQLite:

```
DATABASE_URL=sqlite:///./taskpilot.db
```

### Storage (S3-compatible)

| Variable         | Description         | Example                         |
| ---------------- | ------------------- | ------------------------------- |
| `S3_ENDPOINT`    | S3 endpoint URL     | `https://s3.amazonaws.com`      |
| `S3_BUCKET`      | Bucket name         | `taskpilot-artifacts`           |
| `S3_ACCESS_KEY`  | Access key          | `AKIA...`                       |
| `S3_SECRET_KEY`  | Secret key          | `wJal...`                       |

### Auth

| Variable         | Description                                  | Example           |
| ---------------- | -------------------------------------------- | ----------------- |
| `SECRET_KEY`     | Used to sign JWT tokens                      | (random string)   |
| `ALGORITHM`      | JWT signing algorithm                        | `HS256`           |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes       | `60`              |
| `JWT_SECRET`     | Alias for SECRET_KEY (frontend cookie auth)  | (random string)   |
| `COOKIE_SECRET`  | Signing key for HTTP-only cookies            | (random string)   |

### OAuth (per provider)

| Variable                  | Description             |
| ------------------------- | ----------------------- |
| `GOOGLE_CLIENT_ID`        | Google OAuth client ID  |
| `GOOGLE_CLIENT_SECRET`    | Google OAuth secret     |
| `SLACK_CLIENT_ID`         | Slack OAuth client ID   |
| `SLACK_CLIENT_SECRET`     | Slack OAuth secret      |
| `NOTION_CLIENT_ID`        | Notion OAuth client ID  |
| `NOTION_CLIENT_SECRET`    | Notion OAuth secret     |

### Payments

| Variable                  | Description                |
| ------------------------- | -------------------------- |
| `STRIPE_API_KEY`          | Stripe secret key          |
| `STRIPE_WEBHOOK_SECRET`   | Stripe webhook signing key |

### AI Providers

| Variable         | Description                  | Example   |
| ---------------- | ---------------------------- | --------- |
| `LLM_PROVIDER`   | Which LLM backend to use    | `openai`  |
| `OPENAI_API_KEY`  | OpenAI API key              | `sk-...`  |

---

## Starting the Development Servers

### Backend (FastAPI)

```bash
cd backend
source .venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now available at **http://localhost:8000**.

Interactive API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Health check:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### Frontend (Next.js)

```bash
cd frontend

# Set the API URL
export NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the dev server
npm run dev
```

The web UI is now available at **http://localhost:3000**.

### Running Both at Once (Docker Compose)

From the project root:

```bash
docker compose up --build
```

This starts the backend on port 8000 and the frontend on port 3000.

---

## Authentication Flow

TaskPilot uses **JWT (JSON Web Token)** authentication. The full flow is:

### 1. Sign Up

```bash
curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecureP@ss1",
    "name": "Alice"
  }'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Signing up automatically creates a **personal organisation** and grants the `OWNER` role.

### 2. Log In

```bash
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecureP@ss1"
  }'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 3. Authenticated Requests

Include the token in the `Authorization` header for every subsequent request:

```bash
export TOKEN="eyJhbGciOiJIUzI1NiIs..."

curl -s http://localhost:8000/api/me \
  -H "Authorization: Bearer $TOKEN"
```

### Token Lifecycle

| Event          | Behaviour                                   |
| -------------- | ------------------------------------------- |
| Signup         | Returns a fresh JWT                         |
| Login          | Returns a fresh JWT                         |
| Expiry         | Token expires after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60 min) |
| Invalid token  | API returns `401 Unauthorized`              |

---

## Using the API

All endpoints are prefixed with `/api`. Authenticated endpoints require the `Authorization: Bearer <token>` header.

### Health Check

```bash
curl http://localhost:8000/health
```

### Auth Endpoints

#### POST /api/auth/signup

Create a new account. Returns a JWT.

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"MyP@ssw0rd","name":"Bob"}'
```

#### POST /api/auth/login

Log in with existing credentials. Returns a JWT.

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"MyP@ssw0rd"}'
```

### User Endpoints

#### GET /api/me

Get the current user's profile.

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/me
```

Response:

```json
{
  "id": "uuid",
  "email": "bob@example.com",
  "name": "Bob",
  "org_id": "uuid",
  "role": "OWNER"
}
```

### Integration Endpoints

#### GET /api/integrations

List all available integrations (no auth required).

```bash
curl http://localhost:8000/api/integrations
```

Response:

```json
[
  {
    "provider": "google",
    "name": "Google Workspace",
    "description": "Gmail, Sheets, Drive, Calendar",
    "auth_type": "oauth2"
  },
  {
    "provider": "slack",
    "name": "Slack",
    "description": "Messaging and notifications",
    "auth_type": "oauth2"
  }
]
```

#### GET /api/connections

List your organisation's active connections.

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/connections
```

#### POST /api/connections/{provider}/start

Start an OAuth flow for a provider.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/connections/google/start
```

Response:

```json
{
  "authorize_url": "https://oauth.example.com/google/authorize?connection_id=uuid",
  "connection_id": "uuid"
}
```

### Workflow Endpoints

#### GET /api/workflows

List all workflows in your organisation.

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/workflows
```

#### POST /api/workflows

Create a new workflow.

```bash
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Revenue Report",
    "description": "Pull Stripe data and post to Slack",
    "definition": {
      "steps": [
        {
          "id": "s1",
          "tool": "stripe.payments.list",
          "args": {"start_date": "2024-01-01", "end_date": "2024-01-07"}
        },
        {
          "id": "s2",
          "tool": "slack.chat.postMessage",
          "args": {"channel": "#finance", "text": "Revenue report ready."}
        }
      ]
    }
  }'
```

#### POST /api/workflows/{workflow_id}/run

Execute a workflow.

```bash
curl -X POST http://localhost:8000/api/workflows/<workflow_id>/run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"slack_channel": "#finance"}}'
```

### Run Endpoints

#### GET /api/runs/{run_id}

Get run details, including step-by-step status.

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/runs/<run_id>
```

Response:

```json
{
  "id": "uuid",
  "workflow_version_id": "uuid",
  "org_id": "uuid",
  "status": "COMPLETED",
  "initiated_by": "uuid",
  "input_json": {},
  "output_summary": "Posted weekly revenue report to Slack.",
  "started_at": "2024-01-15T10:00:00Z",
  "finished_at": "2024-01-15T10:00:05Z",
  "steps": [
    {
      "id": "uuid",
      "step_index": 0,
      "tool": "stripe.payments.list",
      "status": "COMPLETED",
      "input_json": {},
      "output_json": {},
      "error": null,
      "started_at": "2024-01-15T10:00:00Z",
      "finished_at": "2024-01-15T10:00:02Z"
    }
  ]
}
```

#### POST /api/runs/{run_id}/cancel

Cancel a queued or running workflow run.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/runs/<run_id>/cancel
```

### Template Endpoints

#### GET /api/templates

List available workflow templates.

```bash
curl http://localhost:8000/api/templates
```

Response:

```json
[
  {
    "id": "clean_inbox",
    "name": "Clean Inbox",
    "description": "Summarize and label billing emails; draft responses for missing invoices.",
    "tags": ["email", "ops"],
    "definition": { "..." : "..." }
  },
  {
    "id": "weekly_revenue_report",
    "name": "Weekly Revenue Report",
    "description": "Pull weekly Stripe revenue, update Google Sheet, generate PDF, post to Slack.",
    "tags": ["finance", "reporting", "weekly"],
    "definition": { "..." : "..." }
  }
]
```

### Billing Endpoints

#### POST /api/billing/webhook

Stripe webhook endpoint. Stripe sends events here automatically.

```bash
curl -X POST http://localhost:8000/api/billing/webhook \
  -H "Content-Type: application/json" \
  -d '{"type":"checkout.session.completed","data":{}}'
```

### Admin Endpoints

All admin endpoints require the `OWNER` or `ADMIN` role.

#### GET /api/admin/members

List organisation members.

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/admin/members
```

#### POST /api/admin/members/invite

Invite a new member to the organisation.

```bash
curl -X POST http://localhost:8000/api/admin/members/invite \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "carol@example.com", "role": "MEMBER"}'
```

#### GET /api/admin/policies

Get the organisation's approval policies.

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/admin/policies
```

Response:

```json
{
  "require_approval_for_write": true
}
```

#### PUT /api/admin/policies

Update the organisation's approval policies.

```bash
curl -X PUT http://localhost:8000/api/admin/policies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"require_approval_for_write": false}'
```

---

## Using the Web UI

The TaskPilot frontend is a Next.js application served at **http://localhost:3000** during development.

### Pages

| Page               | Path                | Description                                                |
| ------------------ | ------------------- | ---------------------------------------------------------- |
| **Home**           | `/`                 | Landing page with overview of TaskPilot                    |
| **Sign Up**        | `/signup`           | Create a new account                                       |
| **Log In**         | `/login`            | Log in with email and password                             |
| **Chat**           | `/chat`             | Natural-language interface — describe a task and TaskPilot builds a workflow |
| **Workflows**      | `/workflows`        | List, create, and manage workflows                         |
| **Workflow Detail** | `/workflows/[id]`  | View a single workflow's definition, versions, and runs    |
| **Runs**           | `/runs`             | View all workflow runs for the organisation                |
| **Run Detail**     | `/runs/[id]`        | Step-by-step run progress with logs and outputs            |
| **Templates**      | `/templates`        | Browse and use pre-built workflow templates                 |
| **Integrations**   | `/integrations`     | Connect third-party services (Google, Slack, Stripe, etc.) |
| **Billing**        | `/billing`          | Manage subscription and view usage                         |
| **Admin**          | `/admin`            | Manage organisation members and approval policies          |

### Typical User Flow

1. **Sign up** at `/signup`.
2. **Connect integrations** at `/integrations` (e.g., Google, Slack).
3. **Create a workflow** — either from a template at `/templates`, or by describing a task in natural language at `/chat`.
4. **Run the workflow** from the workflow detail page or via the API.
5. **Monitor the run** at `/runs/[id]` to see step-by-step progress.
6. **Review outputs** — artifacts, summaries, and logs.

---

## Database Setup and Migrations

### Local Development (SQLite)

By default, TaskPilot uses SQLite for local development. The database file is created automatically at `backend/taskpilot.db` when you first start the server.

No setup is required.

### Production (PostgreSQL)

1. **Create the database:**

```bash
createdb taskpilot
```

2. **Set the connection string:**

```bash
# In backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/taskpilot
```

3. **Run migrations with Alembic:**

```bash
cd backend
source .venv/bin/activate

# Generate the initial migration (if not already present)
alembic revision --autogenerate -m "initial"

# Apply all migrations
alembic upgrade head
```

4. **Verify the schema:**

```bash
psql -d taskpilot -c "\dt"
```

You should see tables: `users`, `orgs`, `memberships`, `connections`, `workflows`, `workflow_versions`, `schedules`, `runs`, `run_steps`, `artifacts`, `usage_events`, `subscriptions`.

### Creating New Migrations

When you change models in `backend/app/models.py`:

```bash
cd backend
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

### Resetting the Database (Development Only)

```bash
cd backend
rm -f taskpilot.db
alembic upgrade head
```

Or simply delete the SQLite file and restart the server — tables are recreated automatically.
