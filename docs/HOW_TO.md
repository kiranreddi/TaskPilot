# TaskPilot — How-To Guide

> Step-by-step instructions for common TaskPilot operations.

---

## Table of Contents

1. [How to Create a Workflow](#how-to-create-a-workflow)
2. [How to Run a Workflow](#how-to-run-a-workflow)
3. [How to Connect Integrations](#how-to-connect-integrations)
4. [How to Manage Templates](#how-to-manage-templates)
5. [How to Configure Approval Policies](#how-to-configure-approval-policies)
6. [How to Manage Org Members](#how-to-manage-org-members)
7. [How to View Run History](#how-to-view-run-history)
8. [How to Cancel a Run](#how-to-cancel-a-run)
9. [How to Set Up Billing](#how-to-set-up-billing)
10. [How to Deploy to Production](#how-to-deploy-to-production)

---

## How to Create a Workflow

There are three ways to create a workflow in TaskPilot.

### Option A — Natural Language (Chat)

1. Navigate to **http://localhost:3000/chat** in the web UI.
2. Describe the task in plain English, for example:

   > "Pull Stripe revenue for last week, append it to my weekly revenue Google Sheet, generate a PDF report, and post it in Slack #finance."

3. TaskPilot's LLM generates a step-by-step workflow definition.
4. Review the generated steps and click **Save Workflow**.

### Option B — From a Template

1. Navigate to **http://localhost:3000/templates**.
2. Browse the available templates (e.g., *Clean Inbox*, *Weekly Revenue Report*).
3. Click **Use Template** on the one you want.
4. Customise the inputs (e.g., change the Slack channel or date range).
5. Click **Create Workflow**.

### Option C — Via the API

```bash
# Authenticate first
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"SecureP@ss1"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Create the workflow
curl -s -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Standup Summary",
    "description": "Summarise Jira tickets and post to Slack",
    "definition": {
      "steps": [
        {
          "id": "s1",
          "tool": "taskpilot.llm.summarize",
          "args": {"items_ref": "input", "style": "default"}
        }
      ]
    }
  }' | python3 -m json.tool
```

### Workflow Definition Format

A workflow definition is a JSON object with a `steps` array. Each step has:

| Field   | Type   | Description                                  |
| ------- | ------ | -------------------------------------------- |
| `id`    | string | Unique step identifier (e.g., `s1`, `s2`)    |
| `name`  | string | Human-readable step name (optional)          |
| `tool`  | string | Tool to execute (e.g., `stripe.payments.list`) |
| `risk`  | string | Risk level: `READ` or `WRITE` (optional)     |
| `args`  | object | Arguments passed to the tool                 |

Steps can reference outputs from previous steps using `<step_id>.output` notation:

```json
{
  "steps": [
    {"id": "s1", "tool": "stripe.payments.list", "args": {"start_date": "2024-01-01"}},
    {"id": "s2", "tool": "taskpilot.data.aggregate", "args": {"input_ref": "s1.output"}}
  ]
}
```

---

## How to Run a Workflow

### Via the Web UI

1. Go to **http://localhost:3000/workflows**.
2. Click on the workflow you want to run.
3. On the workflow detail page, click **Run Workflow**.
4. Optionally provide input overrides (e.g., a different date range).
5. Click **Confirm** to start the run.
6. You are redirected to the run detail page to watch progress.

### Via the API

```bash
# Get the workflow ID
WORKFLOW_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/workflows \
  | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")

# Run it
curl -s -X POST "http://localhost:8000/api/workflows/$WORKFLOW_ID/run" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"slack_channel": "#finance"}}' \
  | python3 -m json.tool
```

### Run with Approval Token

If the organisation requires approval for write operations, the first run may pause at write steps. Re-run with an approval token:

```bash
curl -s -X POST "http://localhost:8000/api/workflows/$WORKFLOW_ID/run" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {"slack_channel": "#finance"},
    "approval_token": "approve-all"
  }' | python3 -m json.tool
```

### Run Statuses

| Status       | Meaning                                |
| ------------ | -------------------------------------- |
| `QUEUED`     | Run is waiting to be picked up         |
| `RUNNING`    | Run is currently executing             |
| `COMPLETED`  | All steps finished successfully        |
| `FAILED`     | One or more steps encountered an error |
| `CANCELED`   | Run was cancelled by the user          |
| `NEEDS_APPROVAL` | Paused, waiting for human approval |

---

## How to Connect Integrations

TaskPilot supports OAuth2-based integrations with third-party services.

### Available Integrations

| Provider  | Name              | Capabilities                          |
| --------- | ----------------- | ------------------------------------- |
| `google`  | Google Workspace  | Gmail, Sheets, Drive, Calendar        |
| `slack`   | Slack             | Messaging and notifications           |
| `stripe`  | Stripe            | Payment processing and billing data   |
| `notion`  | Notion            | Notes and documentation               |
| `hubspot` | HubSpot           | CRM and marketing automation          |

### Via the Web UI

1. Go to **http://localhost:3000/integrations**.
2. Find the integration you want to connect.
3. Click **Connect**.
4. You are redirected to the provider's OAuth consent screen.
5. Grant the requested permissions.
6. You are redirected back to TaskPilot with the connection active.

### Via the API

```bash
# List available integrations
curl -s http://localhost:8000/api/integrations | python3 -m json.tool

# Start OAuth flow for Google
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/connections/google/start \
  | python3 -m json.tool
```

Response:

```json
{
  "authorize_url": "https://oauth.example.com/google/authorize?connection_id=abc-123",
  "connection_id": "abc-123"
}
```

Open the `authorize_url` in your browser to complete the OAuth flow.

### Check Connected Services

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/connections | python3 -m json.tool
```

---

## How to Manage Templates

Templates are pre-built workflow definitions that can be used as starting points.

### Browsing Templates

**Web UI:** Go to **http://localhost:3000/templates** to see all available templates.

**API:**

```bash
curl -s http://localhost:8000/api/templates | python3 -m json.tool
```

### Built-in Templates

TaskPilot ships with two built-in templates:

1. **Clean Inbox** (`clean_inbox`)
   - Searches Gmail for billing emails from the last 14 days
   - Summarises totals by vendor
   - Applies the `TaskPilot/Billing` label
   - Drafts follow-up emails for missing invoices

2. **Weekly Revenue Report** (`weekly_revenue_report`)
   - Fetches Stripe payments for a date range
   - Aggregates totals by currency and source
   - Updates a Google Sheet
   - Generates a PDF report
   - Posts the report to a Slack channel

### Creating a Workflow from a Template

**Via the API:**

```bash
curl -s -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Revenue Report",
    "description": "Based on the weekly revenue report template",
    "template_id": "weekly_revenue_report"
  }' | python3 -m json.tool
```

### Adding Custom Templates

Templates are loaded from JSON files in the project root directory. To add a new template:

1. Create a JSON file following the workflow schema (see `docs/Workflow_Schema.md`).
2. Place it in the project root directory.
3. Register it in `backend/app/routers/templates.py` by adding an entry to the `template_files` list.
4. Restart the backend server.

---

## How to Configure Approval Policies

Approval policies control whether write operations (e.g., sending emails, updating spreadsheets, posting messages) require human approval before execution.

### View Current Policies

**Web UI:** Go to **http://localhost:3000/admin** → **Policies** section.

**API (requires OWNER or ADMIN role):**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/policies | python3 -m json.tool
```

Response:

```json
{
  "require_approval_for_write": true
}
```

### Update Policies

**API:**

```bash
curl -s -X PUT http://localhost:8000/api/admin/policies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"require_approval_for_write": false}' | python3 -m json.tool
```

### How Approval Works

1. When `require_approval_for_write` is `true` (the default), any workflow step with `risk: "WRITE"` will pause the run.
2. The run status changes to `NEEDS_APPROVAL`.
3. An admin or the workflow initiator can approve the pending step.
4. Once approved, the run continues from where it paused.

**Tip:** For development and testing, set `require_approval_for_write` to `false` so runs complete immediately.

---

## How to Manage Org Members

Organisations (orgs) are the top-level container in TaskPilot. Every user belongs to at least one org.

### Roles

| Role     | Permissions                                              |
| -------- | -------------------------------------------------------- |
| `OWNER`  | Full access, can manage members, policies, and billing   |
| `ADMIN`  | Can manage members and policies, cannot transfer ownership |
| `MEMBER` | Can create and run workflows, connect integrations       |
| `VIEWER` | Read-only access to workflows, runs, and templates       |

### List Members

**Web UI:** Go to **http://localhost:3000/admin** → **Members** section.

**API (requires OWNER or ADMIN):**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/members | python3 -m json.tool
```

Response:

```json
[
  {
    "id": "membership-uuid",
    "user_id": "user-uuid",
    "org_id": "org-uuid",
    "role": "OWNER",
    "email": "alice@example.com",
    "name": "Alice"
  }
]
```

### Invite a New Member

**API:**

```bash
curl -s -X POST http://localhost:8000/api/admin/members/invite \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "carol@example.com", "role": "MEMBER"}' \
  | python3 -m json.tool
```

If the user does not already have a TaskPilot account, one is created automatically. The user can then log in and will see the organisation's workflows.

---

## How to View Run History

### Via the Web UI

1. Go to **http://localhost:3000/runs**.
2. You see a list of all runs for your organisation, sorted by most recent.
3. Click a run to see the detail page with:
   - Overall status (QUEUED, RUNNING, COMPLETED, FAILED, CANCELED)
   - Step-by-step breakdown with individual status, inputs, outputs, and errors
   - Timestamps for start and finish
   - Output summary and artifacts

### Via the API

**Get a specific run:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/runs/<run_id> | python3 -m json.tool
```

The response includes the full `steps` array so you can inspect each step's `status`, `input_json`, `output_json`, and `error` fields.

### Interpreting Step Statuses

| Step Status  | Meaning                          |
| ------------ | -------------------------------- |
| `QUEUED`     | Step has not started yet         |
| `RUNNING`    | Step is currently executing      |
| `COMPLETED`  | Step finished successfully       |
| `FAILED`     | Step encountered an error        |
| `SKIPPED`    | Step was skipped (conditional)   |

---

## How to Cancel a Run

You can cancel a run that is in `QUEUED` or `RUNNING` status.

### Via the Web UI

1. Go to **http://localhost:3000/runs/<run_id>**.
2. Click the **Cancel Run** button (visible only if the run is active).
3. Confirm the cancellation.

### Via the API

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/runs/<run_id>/cancel | python3 -m json.tool
```

Response:

```json
{
  "id": "run-uuid",
  "status": "CANCELED",
  "..."
}
```

### Notes

- Cancelling a run is permanent — it cannot be resumed.
- Steps that have already completed remain completed; only pending steps are skipped.
- Attempting to cancel a run that is already `COMPLETED`, `FAILED`, or `CANCELED` returns a `400 Bad Request`.

---

## How to Set Up Billing

TaskPilot uses **Stripe** for subscription management and usage-based billing.

### Prerequisites

1. A Stripe account (https://stripe.com).
2. Your Stripe API key and webhook signing secret.

### 1. Configure Stripe Keys

Add the following to your `backend/.env`:

```bash
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 2. Set Up the Webhook

In the Stripe Dashboard:

1. Go to **Developers → Webhooks**.
2. Click **Add endpoint**.
3. Set the URL to `https://your-api-domain.com/api/billing/webhook`.
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Click **Add endpoint**.

### 3. Local Testing with Stripe CLI

```bash
# Install the Stripe CLI
brew install stripe/stripe-cli/stripe

# Forward webhook events to your local server
stripe listen --forward-to http://localhost:8000/api/billing/webhook

# The CLI prints a webhook signing secret — use it in your .env
```

### 4. Manage Subscription via the Web UI

1. Go to **http://localhost:3000/billing**.
2. View your current plan, usage, and invoices.
3. Click **Upgrade** to change your subscription plan.

### Plans

| Plan       | Included            | Overage          |
| ---------- | ------------------- | ---------------- |
| **Free**   | 100 runs/month      | Not available    |
| **Pro**    | 1,000 runs/month    | $0.01 per run    |
| **Team**   | 10,000 runs/month   | $0.005 per run   |

---

## How to Deploy to Production

For detailed deployment instructions, see:

- **Frontend:** [docs/DEPLOYMENT_FRONTEND.md](./DEPLOYMENT_FRONTEND.md) — Cloudflare Pages deployment guide
- **Backend:** [docs/DEPLOYMENT_BACKEND.md](./DEPLOYMENT_BACKEND.md) — Multiple deployment options

### Quick Overview

1. **Frontend** → Deploy to **Cloudflare Pages** via Git integration or Wrangler CLI.
2. **Backend** → Deploy to **Railway**, **Fly.io**, or any container platform using the provided `backend/Dockerfile`.
3. **Database** → Use a managed **PostgreSQL** instance (e.g., Supabase, Neon, Railway Postgres).
4. **Redis** → Use a managed Redis instance (e.g., Upstash, Railway Redis).

### Using Docker Compose (Self-Hosted)

```bash
# From the project root
docker compose up --build -d

# Verify
curl http://localhost:8000/health
curl http://localhost:3000
```

See the `docker-compose.yml` in the project root for the full configuration.
