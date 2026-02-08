# UX Wireframes (text) — TaskPilot

## 0) Global nav
Left sidebar:
- Chat
- Workflows
- Templates
- Runs
- Integrations
- Billing
- Admin (role-gated)

## 1) Auth
### 1.1 Sign up
[ TaskPilot ]
Email [____]
Password [____]
Name [____]
[Create account]
[Continue with Google]

## 2) Integrations
### 2.1 Integrations catalog
Search [____]
Cards:
- Google Workspace  [Connect]
- Slack             [Connect]
- Notion            [Connect]
- Stripe            [Connect]
- HubSpot           [Connect]

### 2.2 Connection details
Google Workspace — Connected ✅
Scopes: gmail.read, calendar.write, drive.read
Last healthy: 2 mins ago
[Reconnect] [Disconnect]

## 3) Chat / Task
### 3.1 Chat home
Prompt box:
“Ask TaskPilot to do something across your apps…”
Toggle: Read-only mode [ON/OFF]
Apps chips: [Google] [Slack] [Notion] [Stripe] (optional)
[Run]

### 3.2 Plan preview modal (before execution)
Title: “Here’s what I will do”
Steps:
1) Search Gmail for billing emails (READ)
2) Summarize totals by vendor (READ)
3) Post summary to Slack #finance (WRITE)  ⚠ requires approval
Buttons:
[Approve & Run]  [Edit]  [Cancel]

### 3.3 Run progress
Timeline:
- Step 1 running…
- Step 1 done ✅
- Step 2 running…
Artifacts:
- summary.md
- report.pdf

## 4) Workflows
### 4.1 Workflow list
Rows: Name | Tags | Last run | Status | [Run] [Edit]

### 4.2 Workflow editor
Name, description
Inputs (key/value schema)
Steps list (drag reorder)
- Step card: tool, args, risk, retry policy
Buttons: [Save new version] [Test run]

### 4.3 Scheduling
Cron picker + timezone
[Enable schedule]

## 5) Templates
Grid of templates:
- Weekly revenue report (Stripe → Sheets → PDF → Slack)
- Clean inbox (Gmail)
- Meeting follow-ups (Calendar → Notion → Slack)
[Use]

## 6) Runs
Runs table:
Run ID | Workflow | Status | Started | Duration | [View]
Run detail shows:
- step logs (redacted)
- retry history
- outputs & artifacts

## 7) Billing
Plan card + usage meters
Runs this month: 142 / 500
Tokens: 1.2M / 3M
[Upgrade] [Manage billing]

## 8) Admin
- Org members (invite/remove, role change)
- Policy settings:
  - Require approval for WRITE actions (default ON)
  - Allowed email domains list
- Integration health dashboard
