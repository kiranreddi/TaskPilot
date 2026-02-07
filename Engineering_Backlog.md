# Engineering Backlog (Epics → Stories)

## Epic 1: Auth + Orgs
- Signup/login + Google OAuth
- Org creation, membership invites
- RBAC middleware + tenant isolation tests

## Epic 2: Integrations Framework
- OAuth state + callback handlers
- Token encryption + refresh scheduler
- Connector interface + tool registry

## Epic 3: Orchestrator Runtime (Temporal)
- WorkflowRun Temporal workflow
- Activities: Planner, ExecuteTool, Verify, Notify
- Run events streaming (SSE)

## Epic 4: UI Screens
- Integrations page
- Chat + plan preview
- Runs dashboard + run detail
- Workflows list + editor
- Templates library

## Epic 5: Billing + Metering
- Stripe checkout + portal
- Usage events pipeline
- Quota enforcement + upgrade UX

## Epic 6: Admin + Policies
- Org settings, approval policies
- Allowed domains list for outbound email
- Integration health dashboard

## Epic 7: Hardening
- Rate limiting, caching
- Redaction, audit export
- Load testing + incident runbooks
