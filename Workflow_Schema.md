# Workflow Schema — TaskPilot

## 1) Concepts
A workflow is a versioned JSON definition that executes as a DAG (initially linear steps).
Each step calls a tool (connector action) with a strict JSON schema.

## 2) Workflow JSON (high-level)
- metadata: name, description, tags
- inputs: variable definitions
- steps: ordered list of steps
- policies: approvals required, allowed domains, read-only mode default
- outputs: what to show user

## 3) Example workflow (linear)
See `templates/weekly_revenue_report.json`.

## 4) Step schema (conceptual)
- id: string
- name: string
- tool: string (e.g., google.gmail.search, stripe.list_payments)
- args: object (validated per tool)
- risk: READ | WRITE | DESTRUCTIVE
- depends_on: [step_id]
- on_error: RETRY | STOP | CONTINUE | MANUAL_REVIEW

## 5) Tool registry contract
Each connector exposes tools with:
- name
- description
- input_schema (JSON schema)
- output_schema (JSON schema)
- risk_level
- idempotency_support (bool)

## 6) Approval gates
Policy engine blocks execution if:
- risk_level >= WRITE and no approval token provided for that run
- action targets outside allowed domain lists (email recipient domain, etc.)

## 7) Versioning
Any edit creates a new workflow_version record.
Runs reference a workflow_version immutably.
