# TaskPilot — Examples & Demos

> Hands-on examples showing TaskPilot in action — from quick start to full API sessions.

---

## Table of Contents

1. [Quick Start (5-Minute Demo)](#quick-start-5-minute-demo)
2. [Example 1: Weekly Revenue Report](#example-1-weekly-revenue-report)
3. [Example 2: Clean Inbox](#example-2-clean-inbox)
4. [Example 3: Custom Workflow Creation](#example-3-custom-workflow-creation)
5. [Full API Session Lifecycle](#full-api-session-lifecycle)
6. [Example Prompts for Natural Language Workflows](#example-prompts-for-natural-language-workflows)

---

## Quick Start (5-Minute Demo)

This demo walks you through signup, creating a workflow, and running it — all from the command line.

### Prerequisites

- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3000` (optional for this demo)

### Step 1 — Health Check

```bash
curl -s http://localhost:8000/health
```

```json
{"status": "ok"}
```

### Step 2 — Sign Up

```bash
curl -s -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "DemoP@ss123",
    "name": "Demo User"
  }'
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Save the token:

```bash
export TOKEN="eyJhbGciOiJIUzI1NiIs..."
```

### Step 3 — Verify Your Identity

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/me
```

```json
{
  "id": "a1b2c3d4-...",
  "email": "demo@example.com",
  "name": "Demo User",
  "org_id": "e5f6a7b8-...",
  "role": "OWNER"
}
```

### Step 4 — Create a Simple Workflow

```bash
curl -s -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hello World",
    "description": "A simple summarization workflow",
    "definition": {
      "steps": [
        {
          "id": "s1",
          "tool": "taskpilot.llm.summarize",
          "args": {"items_ref": "input", "style": "default"}
        }
      ]
    }
  }'
```

```json
{
  "id": "wf-uuid-...",
  "org_id": "e5f6a7b8-...",
  "name": "Hello World",
  "description": "A simple summarization workflow",
  "status": "ACTIVE",
  "created_by": "a1b2c3d4-...",
  "created_at": "2024-01-15T12:00:00Z"
}
```

### Step 5 — Run It

```bash
curl -s -X POST http://localhost:8000/api/workflows/wf-uuid-.../run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

### Step 6 — Check the Result

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/runs/<run_id> | python3 -m json.tool
```

**Done!** You signed up, created a workflow, ran it, and checked the results — all in under 5 minutes.

---

## Example 1: Weekly Revenue Report

This example recreates the built-in **Weekly Revenue Report** template step by step.

### What It Does

1. Fetches Stripe payments for a date range
2. Aggregates totals by currency and source
3. Updates a Google Sheet with the results
4. Generates a PDF report
5. Posts the report to a Slack channel

### Step 1 — Authenticate

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"DemoP@ss123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

### Step 2 — Connect Required Integrations

```bash
# Connect Stripe
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/connections/stripe/start | python3 -m json.tool

# Connect Google (for Sheets)
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/connections/google/start | python3 -m json.tool

# Connect Slack
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/connections/slack/start | python3 -m json.tool
```

### Step 3 — Create the Workflow

```bash
curl -s -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Revenue Report",
    "description": "Pull weekly Stripe revenue, update Google Sheet, generate PDF, post to Slack.",
    "definition": {
      "steps": [
        {
          "id": "s1",
          "name": "Fetch Stripe payments for date range",
          "tool": "stripe.payments.list",
          "risk": "READ",
          "args": {
            "start_date": "2024-01-08",
            "end_date": "2024-01-14"
          }
        },
        {
          "id": "s2",
          "name": "Aggregate totals by currency and source",
          "tool": "taskpilot.data.aggregate",
          "risk": "READ",
          "args": {
            "input_ref": "s1.output",
            "group_by": ["currency", "source"],
            "sum": ["amount"]
          }
        },
        {
          "id": "s3",
          "name": "Update Google Sheet",
          "tool": "google.sheets.append_rows",
          "risk": "WRITE",
          "args": {
            "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms",
            "sheet_name": "Weekly",
            "rows_ref": "s2.output.rows"
          }
        },
        {
          "id": "s4",
          "name": "Generate PDF report",
          "tool": "taskpilot.report.pdf",
          "risk": "READ",
          "args": {
            "template": "weekly_revenue",
            "data_ref": "s2.output",
            "title": "Weekly Revenue Report"
          }
        },
        {
          "id": "s5",
          "name": "Post report to Slack",
          "tool": "slack.chat.postMessage",
          "risk": "WRITE",
          "args": {
            "channel": "#finance",
            "text": "Weekly revenue report attached.",
            "file_ref": "s4.output.file"
          }
        }
      ]
    }
  }' | python3 -m json.tool
```

Save the workflow ID from the response:

```bash
WORKFLOW_ID="<id from response>"
```

### Step 4 — Disable Approval (for Testing)

```bash
curl -s -X PUT http://localhost:8000/api/admin/policies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"require_approval_for_write": false}'
```

### Step 5 — Run the Workflow

```bash
curl -s -X POST "http://localhost:8000/api/workflows/$WORKFLOW_ID/run" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "week_start": "2024-01-08",
      "week_end": "2024-01-14",
      "slack_channel": "#finance"
    }
  }' | python3 -m json.tool
```

### Step 6 — Check Run Status

```bash
RUN_ID="<id from response>"

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/runs/$RUN_ID" | python3 -m json.tool
```

Expected output:

```json
{
  "id": "run-uuid",
  "status": "COMPLETED",
  "output_summary": "Posted weekly revenue report to Slack and appended results to Google Sheet.",
  "steps": [
    {"step_index": 0, "tool": "stripe.payments.list", "status": "COMPLETED"},
    {"step_index": 1, "tool": "taskpilot.data.aggregate", "status": "COMPLETED"},
    {"step_index": 2, "tool": "google.sheets.append_rows", "status": "COMPLETED"},
    {"step_index": 3, "tool": "taskpilot.report.pdf", "status": "COMPLETED"},
    {"step_index": 4, "tool": "slack.chat.postMessage", "status": "COMPLETED"}
  ]
}
```

---

## Example 2: Clean Inbox

This example recreates the built-in **Clean Inbox** template step by step.

### What It Does

1. Searches Gmail for billing-related emails from the last 14 days
2. Summarises totals by vendor using an LLM
3. Applies the `TaskPilot/Billing` label to matching messages
4. Drafts follow-up emails for missing invoices (without sending)

### Step 1 — Authenticate

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"DemoP@ss123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### Step 2 — Connect Google

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/connections/google/start | python3 -m json.tool
```

### Step 3 — Create the Workflow

```bash
curl -s -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clean Inbox",
    "description": "Summarize and label billing emails; draft responses for missing invoices.",
    "definition": {
      "steps": [
        {
          "id": "s1",
          "name": "Search Gmail",
          "tool": "google.gmail.search",
          "risk": "READ",
          "args": {
            "q": "newer_than:14d (invoice OR billing OR receipt)",
            "max_results": 50
          }
        },
        {
          "id": "s2",
          "name": "Summarize by vendor",
          "tool": "taskpilot.llm.summarize",
          "risk": "READ",
          "args": {
            "items_ref": "s1.output.messages",
            "style": "table_by_vendor"
          }
        },
        {
          "id": "s3",
          "name": "Apply label",
          "tool": "google.gmail.label.apply",
          "risk": "WRITE",
          "args": {
            "message_ids_ref": "s1.output.message_ids",
            "label": "TaskPilot/Billing"
          }
        },
        {
          "id": "s4",
          "name": "Draft follow-ups for missing invoices",
          "tool": "taskpilot.llm.draft_emails",
          "risk": "READ",
          "args": {
            "messages_ref": "s1.output.messages",
            "tone": "professional",
            "ask": "Please resend the invoice PDF."
          }
        }
      ]
    }
  }' | python3 -m json.tool
```

### Step 4 — Run the Workflow

```bash
WORKFLOW_ID="<id from response>"

curl -s -X POST "http://localhost:8000/api/workflows/$WORKFLOW_ID/run" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "query": "newer_than:14d (invoice OR billing OR receipt)",
      "label": "TaskPilot/Billing"
    }
  }' | python3 -m json.tool
```

### Step 5 — Check Results

```bash
RUN_ID="<id from response>"

curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/runs/$RUN_ID" | python3 -m json.tool
```

Expected: all 4 steps completed, with a vendor summary and draft emails in the output.

---

## Example 3: Custom Workflow Creation

This example shows how to build a completely custom workflow from scratch — a **Sales Lead Research** pipeline.

### What It Does

1. Fetches new leads from HubSpot
2. Enriches each lead with company information using an LLM
3. Drafts personalised outreach emails (without sending)

### Create and Run

```bash
# Create
curl -s -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Lead Research",
    "description": "Fetch leads, enrich, and draft outreach emails",
    "definition": {
      "steps": [
        {
          "id": "s1",
          "name": "Fetch new leads from HubSpot",
          "tool": "hubspot.contacts.list",
          "risk": "READ",
          "args": {
            "filter": "createdate > last_7_days",
            "limit": 25
          }
        },
        {
          "id": "s2",
          "name": "Enrich leads with company info",
          "tool": "taskpilot.llm.summarize",
          "risk": "READ",
          "args": {
            "items_ref": "s1.output.contacts",
            "style": "company_enrichment"
          }
        },
        {
          "id": "s3",
          "name": "Draft personalised outreach emails",
          "tool": "taskpilot.llm.draft_emails",
          "risk": "READ",
          "args": {
            "messages_ref": "s2.output",
            "tone": "friendly_professional",
            "ask": "Introduce TaskPilot and request a 15-minute call."
          }
        }
      ]
    }
  }' | python3 -m json.tool
```

```bash
# Run
WORKFLOW_ID="<id from response>"
curl -s -X POST "http://localhost:8000/api/workflows/$WORKFLOW_ID/run" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

---

## Full API Session Lifecycle

This is a complete end-to-end API session showing the full lifecycle: **signup → explore → create workflow → run → check results → cancel**.

```bash
#!/usr/bin/env bash
set -euo pipefail

API="http://localhost:8000"

echo "=== 1. Health Check ==="
curl -s "$API/health"
echo

echo "=== 2. Sign Up ==="
SIGNUP_RESP=$(curl -s -X POST "$API/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lifecycle@example.com",
    "password": "LifeP@ss99",
    "name": "Lifecycle Demo"
  }')
echo "$SIGNUP_RESP" | python3 -m json.tool
TOKEN=$(echo "$SIGNUP_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "=== 3. Who Am I? ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API/api/me" | python3 -m json.tool

echo "=== 4. List Available Integrations ==="
curl -s "$API/api/integrations" | python3 -m json.tool

echo "=== 5. Connect Google ==="
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  "$API/api/connections/google/start" | python3 -m json.tool

echo "=== 6. List Connections ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API/api/connections" | python3 -m json.tool

echo "=== 7. Browse Templates ==="
curl -s "$API/api/templates" | python3 -m json.tool

echo "=== 8. Create a Workflow ==="
WF_RESP=$(curl -s -X POST "$API/api/workflows" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lifecycle Demo Workflow",
    "description": "End-to-end test workflow",
    "definition": {
      "steps": [
        {
          "id": "s1",
          "tool": "taskpilot.llm.summarize",
          "args": {"items_ref": "input", "style": "default"}
        }
      ]
    }
  }')
echo "$WF_RESP" | python3 -m json.tool
WORKFLOW_ID=$(echo "$WF_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "=== 9. List Workflows ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API/api/workflows" | python3 -m json.tool

echo "=== 10. Run the Workflow ==="
RUN_RESP=$(curl -s -X POST "$API/api/workflows/$WORKFLOW_ID/run" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"message": "Hello, TaskPilot!"}}')
echo "$RUN_RESP" | python3 -m json.tool
RUN_ID=$(echo "$RUN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "=== 11. Check Run Status ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API/api/runs/$RUN_ID" | python3 -m json.tool

echo "=== 12. Invite a Team Member ==="
curl -s -X POST "$API/api/admin/members/invite" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "teammate@example.com", "role": "MEMBER"}' | python3 -m json.tool

echo "=== 13. Check Policies ==="
curl -s -H "Authorization: Bearer $TOKEN" "$API/api/admin/policies" | python3 -m json.tool

echo "=== 14. Create Another Run (to cancel) ==="
RUN2_RESP=$(curl -s -X POST "$API/api/workflows/$WORKFLOW_ID/run" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}')
RUN2_ID=$(echo "$RUN2_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "=== 15. Cancel the Run ==="
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  "$API/api/runs/$RUN2_ID/cancel" | python3 -m json.tool

echo "=== Done! Full lifecycle complete. ==="
```

---

## Example Prompts for Natural Language Workflows

Use these prompts in the **Chat** page (`/chat`) or via the API's natural language workflow creation. TaskPilot's LLM will generate a step-by-step workflow definition from your description.

### 1. Weekly Revenue Report

> "Pull Stripe revenue for last week, append it to my weekly revenue Google Sheet, generate a PDF report, and post it in Slack #finance."

**Generated steps:** Fetch Stripe → Aggregate → Update Sheet → Generate PDF → Post to Slack

### 2. Inbox Clean

> "Find billing-related emails from the last 14 days, summarize totals per vendor, label them 'TaskPilot/Billing', and draft follow-ups for any missing invoices."

**Generated steps:** Search Gmail → Summarize by vendor → Apply label → Draft follow-ups

### 3. Sales Lead Research

> "Find new inbound leads from HubSpot created this week, enrich them with company size and recent news, then draft a personalized outreach email for each (don't send)."

**Generated steps:** Fetch HubSpot contacts → Enrich with LLM → Draft outreach emails

### 4. Project Status Rollup

> "Summarize this week's Jira tickets by status and owner, then post the update in Slack #eng-updates."

**Generated steps:** Fetch Jira tickets → Summarize by status/owner → Post to Slack

### 5. Meeting Follow-Up Automation

> "After each calendar meeting, create a Notion note with summary and action items and assign tasks."

**Generated steps:** Watch Calendar events → Summarize meeting → Create Notion page → Create tasks

---

### Tips for Writing Effective Prompts

| Tip                           | Example                                                |
| ----------------------------- | ------------------------------------------------------ |
| Be specific about data source | "Pull from **Stripe**" not "pull revenue data"         |
| Name the output destination   | "Post to **Slack #finance**"                           |
| Specify time ranges           | "From the **last 7 days**"                             |
| Mention "don't send" for safety | "Draft emails **(don't send)**"                      |
| Use action verbs              | "Summarize", "Aggregate", "Generate", "Post", "Draft" |
