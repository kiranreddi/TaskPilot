# Architecture — TaskPilot

## 1. High-level components
### Frontend (Web)
- Next.js (React + TypeScript)
- Auth UI, Integrations UI, Chat/Task UI, Workflow Builder UI, Runs dashboard, Admin console
- Realtime run updates via SSE/WebSockets

### Backend (Control plane)
- API service (NestJS or FastAPI)
- Responsibilities:
  - auth/orgs/roles
  - workflow CRUD + versioning
  - run initiation + state queries
  - templates
  - billing & metering

### Orchestrator (Data plane)
- Temporal.io (recommended)
- Executes workflow runs as durable workflows with activities:
  - planner activity (LLM)
  - tool execution activities (connectors)
  - verifier activity
  - notifier activity

### Workers
- Connector workers (Google/Slack/Notion/Stripe/etc.)
- LLM worker (planning + verification + summarization)
- Notification worker (email/Slack)

## 2. Data stores
- Postgres: primary system of record
- Redis: caching, rate limits, session caches
- Object storage: artifacts, uploads
- Optional vector store:
  - pgvector or Pinecone (RAG over user docs)

## 3. Key design decisions
### 3.1 Use Temporal for reliability
- Retries and timeouts per step
- Resume after failure
- Timers for schedules
- Idempotency via activity options + your idempotency keys

### 3.2 Split control plane vs data plane
- Control plane: fast CRUD + authorization
- Data plane: long-running runs, retries, connectors, DLQ

### 3.3 Multi-agent pattern
- Planner: generate structured plan (JSON) with tool call schemas
- Executor: run tools
- Verifier: evaluate outputs vs user goal; if uncertain, request clarification
- Summarizer: user-friendly result message and links

## 4. Security
- Encrypt tokens with KMS; never log secrets
- Redact PII and secrets from step inputs/outputs in logs
- Approval policy:
  - default: require explicit confirmation for sending messages/emails, updating records, deleting data
- Tenant isolation enforcement at DB and app layer

## 5. Observability
- OpenTelemetry traces across:
  - API request → Temporal workflow → activities
- Structured logs keyed by:
  - org_id, workflow_id, run_id, step_id
- Alerts: elevated failure rates, OAuth refresh failures, queue backlogs

## 6. Environments
- dev/stage/prod
- Separate OAuth apps per env
- Feature flags for risky features (mass email, bulk deletes)
