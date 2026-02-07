# Data Model — TaskPilot (Postgres)

## 1) Core entities
### users
- id (uuid)
- email (unique)
- name
- password_hash (nullable if OAuth-only)
- created_at

### orgs
- id, name, owner_user_id, created_at

### memberships
- user_id, org_id, role (OWNER/ADMIN/MEMBER/VIEWER)

### connections
- id
- org_id
- provider (google, slack, notion, stripe, hubspot, ...)
- status (CONNECTED/EXPIRED/ERROR)
- scopes (text[])
- token_ciphertext (bytea)  # encrypted blob
- last_ok_at
- created_at

### workflows
- id, org_id, name, description, status (ACTIVE/ARCHIVED)
- created_by, created_at

### workflow_versions
- id, workflow_id, version (int)
- definition_json (jsonb)  # validated against Workflow schema
- created_at

### schedules
- id, workflow_id, cron, timezone, enabled, created_at

### runs
- id
- workflow_version_id
- status (QUEUED/RUNNING/SUCCEEDED/FAILED/CANCELED)
- initiated_by
- input_json (jsonb)
- output_summary (text)
- started_at, finished_at

### run_steps
- id, run_id, step_index
- tool (text)
- status
- input_json (jsonb)  # redacted copy for UI
- output_json (jsonb) # redacted copy for UI
- error (text)
- started_at, finished_at

### artifacts
- id, run_id, type (pdf, csv, doc, link, text)
- storage_url
- metadata_json
- created_at

## 2) Metering/billing
### usage_events
- id, org_id, run_id
- tokens_in, tokens_out
- tool_calls
- timestamp

### subscriptions
- org_id
- stripe_customer_id
- stripe_subscription_id
- plan
- status

## 3) Indices
- memberships(org_id, user_id)
- connections(org_id, provider)
- workflows(org_id)
- runs(workflow_version_id, started_at desc)
- run_steps(run_id, step_index)
