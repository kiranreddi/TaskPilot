# TaskPilot — Backend Deployment Guide

> Deploy the TaskPilot FastAPI backend to production.

---

## Table of Contents

1. [Option 1: Cloudflare Workers](#option-1-cloudflare-workers)
2. [Option 2: Railway.app](#option-2-railwayapp)
3. [Option 3: Fly.io](#option-3-flyio)
4. [Option 4: AWS / GCP / Azure](#option-4-aws--gcp--azure)
5. [Docker Containerization](#docker-containerization)
6. [Database Setup (PostgreSQL)](#database-setup-postgresql)
7. [Redis Setup](#redis-setup)
8. [Environment Variables](#environment-variables)
9. [Health Checks](#health-checks)
10. [SSL/TLS](#ssltls)
11. [Monitoring](#monitoring)

---

## Option 1: Cloudflare Workers

> **⚠️ Limitations:** Cloudflare Workers use the V8 JavaScript runtime, which does **not** natively support Python. Running a FastAPI backend on Workers requires experimental tools that are not production-ready.

### Workarounds

1. **Cloudflare Workers with Python (Beta):** Cloudflare has experimental Python support via Pyodide. However, it does not support all Python packages (e.g., `uvicorn`, `sqlalchemy`, and `bcrypt` are not available).

2. **Use a Worker as a reverse proxy:** Deploy the FastAPI backend elsewhere and use a Cloudflare Worker to proxy requests, add caching, or handle authentication at the edge.

```javascript
// worker.js — Reverse proxy example
export default {
  async fetch(request) {
    const url = new URL(request.url);
    url.hostname = "api-backend.railway.app";
    return fetch(url.toString(), request);
  },
};
```

### Recommendation

**Do not deploy the FastAPI backend directly to Cloudflare Workers.** Use one of the other options below and optionally place a Cloudflare Worker in front for edge caching and DDoS protection.

---

## Option 2: Railway.app

Railway is the easiest way to deploy the TaskPilot backend. It supports Docker, automatic deployments from GitHub, and managed databases.

### Step 1 — Create a Railway Project

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select the **TaskPilot** repository.

### Step 2 — Configure the Backend Service

1. Set the **Root Directory** to `backend`.
2. Railway automatically detects the `Dockerfile` and uses it to build.
3. Alternatively, set the **Start Command** to:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 3 — Add a PostgreSQL Database

1. In the Railway project, click **New** → **Database** → **PostgreSQL**.
2. Railway provisions a Postgres instance and injects `DATABASE_URL` into the environment.

### Step 4 — Add a Redis Instance

1. Click **New** → **Database** → **Redis**.
2. Railway injects `REDIS_URL` into the environment.

### Step 5 — Set Environment Variables

In the backend service settings, add:

```
SECRET_KEY=<random-64-char-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
```

### Step 6 — Deploy

Railway automatically builds and deploys on every push to `main`. Your API is available at `https://your-project.up.railway.app`.

### Step 7 — Custom Domain

1. Go to **Settings** → **Domains**.
2. Click **Add Custom Domain**.
3. Add a CNAME record in your DNS pointing to the Railway domain.

---

## Option 3: Fly.io

Fly.io deploys Docker containers to edge locations worldwide.

### Step 1 — Install the Fly CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh
```

### Step 2 — Authenticate

```bash
fly auth login
```

### Step 3 — Launch the App

```bash
cd backend
fly launch --name taskpilot-api --region iad --no-deploy
```

This creates a `fly.toml` configuration file. Edit it:

```toml
app = "taskpilot-api"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

[checks]
  [checks.health]
    type = "http"
    port = 8000
    path = "/health"
    interval = "15s"
    timeout = "5s"
```

### Step 4 — Create a Postgres Database

```bash
fly postgres create --name taskpilot-db --region iad
fly postgres attach taskpilot-db --app taskpilot-api
```

This automatically sets `DATABASE_URL` in the app's environment.

### Step 5 — Set Secrets

```bash
fly secrets set SECRET_KEY="<random-64-char-string>" \
  ALGORITHM="HS256" \
  ACCESS_TOKEN_EXPIRE_MINUTES="60" \
  STRIPE_API_KEY="sk_live_..." \
  STRIPE_WEBHOOK_SECRET="whsec_..." \
  OPENAI_API_KEY="sk-..." \
  LLM_PROVIDER="openai" \
  --app taskpilot-api
```

### Step 6 — Deploy

```bash
fly deploy --app taskpilot-api
```

### Step 7 — Verify

```bash
curl https://taskpilot-api.fly.dev/health
# {"status": "ok"}
```

---

## Option 4: AWS / GCP / Azure

### AWS (ECS + Fargate)

1. **Push Docker image to ECR:**

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker build -t taskpilot-api ./backend
docker tag taskpilot-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/taskpilot-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/taskpilot-api:latest
```

2. **Create an ECS service:**
   - Cluster: Fargate
   - Task definition: Use the pushed image, port 8000
   - Environment: Set all required env vars
   - Load balancer: Application Load Balancer with HTTPS

3. **Database:** Use Amazon RDS (PostgreSQL).
4. **Redis:** Use Amazon ElastiCache (Redis).

### GCP (Cloud Run)

```bash
cd backend

# Build and push
gcloud builds submit --tag gcr.io/<project-id>/taskpilot-api

# Deploy
gcloud run deploy taskpilot-api \
  --image gcr.io/<project-id>/taskpilot-api \
  --port 8000 \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=postgresql://..." \
  --set-env-vars "SECRET_KEY=..."
```

**Database:** Use Cloud SQL (PostgreSQL).
**Redis:** Use Memorystore (Redis).

### Azure (Container Apps)

```bash
# Create resource group
az group create --name taskpilot-rg --location eastus

# Create container app environment
az containerapp env create --name taskpilot-env --resource-group taskpilot-rg --location eastus

# Deploy
az containerapp create \
  --name taskpilot-api \
  --resource-group taskpilot-rg \
  --environment taskpilot-env \
  --image <acr>.azurecr.io/taskpilot-api:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars "DATABASE_URL=postgresql://..." "SECRET_KEY=..."
```

**Database:** Use Azure Database for PostgreSQL.
**Redis:** Use Azure Cache for Redis.

---

## Docker Containerization

A `Dockerfile` is provided at `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run Locally

```bash
cd backend

# Build
docker build -t taskpilot-api .

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./taskpilot.db \
  -e SECRET_KEY=dev-secret-key \
  taskpilot-api
```

### Multi-Service with Docker Compose

A `docker-compose.yml` is provided at the project root:

```bash
# Start all services
docker compose up --build

# Run in background
docker compose up --build -d

# View logs
docker compose logs -f backend

# Stop
docker compose down
```

This starts:

| Service    | Port | Description          |
| ---------- | ---- | -------------------- |
| `backend`  | 8000 | FastAPI API server   |
| `frontend` | 3000 | Next.js web UI       |

### Production Docker Best Practices

1. **Use multi-stage builds** to reduce image size:

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Run as non-root user:**

```dockerfile
RUN adduser --disabled-password --gecos '' appuser
USER appuser
```

3. **Use `.dockerignore`** to exclude unnecessary files:

```
.venv/
__pycache__/
*.pyc
.env
tests/
*.db
```

---

## Database Setup (PostgreSQL)

### Managed PostgreSQL Providers

| Provider        | Free Tier         | Notes                               |
| --------------- | ----------------- | ----------------------------------- |
| **Neon**        | 512 MB            | Serverless, autoscaling             |
| **Supabase**    | 500 MB            | Built-in Auth, REST API             |
| **Railway**     | $5 credit         | Integrated with Railway deployment  |
| **AWS RDS**     | 750 hours (t2.micro) | 12-month free tier              |
| **GCP Cloud SQL** | $300 credit    | Managed service                     |

### Connection String Format

```
postgresql://user:password@host:5432/taskpilot
```

### Running Migrations

After setting `DATABASE_URL`:

```bash
cd backend
source .venv/bin/activate

# Run pending migrations
alembic upgrade head

# Verify
alembic current
```

### Backup and Restore

```bash
# Backup
pg_dump -Fc $DATABASE_URL > taskpilot_backup.dump

# Restore
pg_restore -d $DATABASE_URL taskpilot_backup.dump
```

---

## Redis Setup

Redis is used for caching, rate limiting, and background job queues.

### Managed Redis Providers

| Provider        | Free Tier            | Notes                      |
| --------------- | -------------------- | -------------------------- |
| **Upstash**     | 10,000 commands/day  | Serverless, REST API       |
| **Railway**     | $5 credit            | Integrated with Railway    |
| **AWS ElastiCache** | 750 hours (t2.micro) | 12-month free tier    |

### Connection String Format

```
redis://user:password@host:6379/0
```

Set it in your environment:

```bash
REDIS_URL=redis://default:password@redis-host:6379/0
```

### Local Redis (Docker)

```bash
docker run -d --name taskpilot-redis -p 6379:6379 redis:7-alpine
```

---

## Environment Variables

The full list of environment variables for production:

| Variable                       | Required | Description                              |
| ------------------------------ | -------- | ---------------------------------------- |
| `DATABASE_URL`                 | Yes      | PostgreSQL connection string             |
| `SECRET_KEY`                   | Yes      | JWT signing key (use a random 64+ char string) |
| `ALGORITHM`                    | No       | JWT algorithm (default: `HS256`)         |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | No       | Token lifetime (default: `60`)           |
| `REDIS_URL`                    | No       | Redis connection string                  |
| `STRIPE_API_KEY`               | No       | Stripe secret key                        |
| `STRIPE_WEBHOOK_SECRET`        | No       | Stripe webhook signing secret            |
| `OPENAI_API_KEY`               | No       | OpenAI API key                           |
| `LLM_PROVIDER`                 | No       | LLM backend (default: `openai`)          |
| `S3_ENDPOINT`                  | No       | S3-compatible storage endpoint           |
| `S3_BUCKET`                    | No       | S3 bucket name                           |
| `S3_ACCESS_KEY`                | No       | S3 access key                            |
| `S3_SECRET_KEY`                | No       | S3 secret key                            |
| `GOOGLE_CLIENT_ID`             | No       | Google OAuth client ID                   |
| `GOOGLE_CLIENT_SECRET`         | No       | Google OAuth client secret               |
| `SLACK_CLIENT_ID`              | No       | Slack OAuth client ID                    |
| `SLACK_CLIENT_SECRET`          | No       | Slack OAuth client secret                |
| `NOTION_CLIENT_ID`             | No       | Notion OAuth client ID                   |
| `NOTION_CLIENT_SECRET`         | No       | Notion OAuth client secret               |

### Generating a Secret Key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Health Checks

The backend exposes a health check endpoint:

```
GET /health
```

Response:

```json
{"status": "ok"}
```

### Configure Health Checks in Your Platform

**Docker Compose:**

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Fly.io:**

```toml
[checks.health]
  type = "http"
  port = 8000
  path = "/health"
  interval = "15s"
  timeout = "5s"
```

**Railway:**
Railway automatically detects the health check endpoint if it returns a 200 status.

**AWS ECS:**

```json
{
  "healthCheck": {
    "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
    "interval": 30,
    "timeout": 5,
    "retries": 3
  }
}
```

---

## SSL/TLS

### Platform-Managed SSL

Most deployment platforms provide automatic SSL:

| Platform       | SSL Setup                                      |
| -------------- | ---------------------------------------------- |
| **Railway**    | Automatic (Let's Encrypt)                      |
| **Fly.io**     | Automatic (Let's Encrypt)                      |
| **Cloudflare** | Automatic (edge certificate)                   |
| **AWS ALB**    | Use ACM (AWS Certificate Manager)              |
| **GCP**        | Managed certificates via Cloud Load Balancing  |

### Custom SSL with Let's Encrypt (Self-Hosted)

If self-hosting, use [Caddy](https://caddyserver.com/) as a reverse proxy for automatic HTTPS:

```
# Caddyfile
api.taskpilot.com {
    reverse_proxy localhost:8000
}
```

Or use **certbot** with Nginx:

```bash
sudo certbot --nginx -d api.taskpilot.com
```

### Force HTTPS

Ensure all HTTP traffic is redirected to HTTPS. Most platforms do this automatically. For self-hosted, add a redirect in your reverse proxy configuration.

---

## Monitoring

### Application-Level Monitoring

1. **Structured Logging:** Use Python's `logging` module with JSON formatting:

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

2. **Request Logging:** FastAPI middleware to log every request:

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} {response.status_code} {duration:.3f}s")
    return response
```

### External Monitoring Services

| Service         | Free Tier          | Integration                         |
| --------------- | ------------------ | ----------------------------------- |
| **Sentry**      | 5K errors/month    | `pip install sentry-sdk[fastapi]`   |
| **Datadog**     | 14-day trial       | APM + logs + metrics                |
| **Grafana Cloud** | 10K metrics      | Prometheus + Loki                   |
| **BetterStack** | 1 monitor          | Uptime + logs                       |

### Sentry Integration

```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    traces_sample_rate=0.1,
)
```

### Uptime Monitoring

Set up an uptime monitor pointing to your health check endpoint:

```
URL:      https://api.taskpilot.com/health
Method:   GET
Interval: 60 seconds
Alert:    Email / Slack when status ≠ 200
```
