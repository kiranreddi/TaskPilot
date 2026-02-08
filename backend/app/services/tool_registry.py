"""Tool/connector registry with built-in tools."""

TOOLS = {
    "google.gmail.search": {
        "name": "google.gmail.search",
        "description": "Search Gmail messages",
        "input_schema": {"q": "string", "max_results": "integer"},
        "output_schema": {"messages": "array", "message_ids": "array"},
        "risk_level": "READ",
    },
    "google.gmail.label.apply": {
        "name": "google.gmail.label.apply",
        "description": "Apply a label to Gmail messages",
        "input_schema": {"message_ids_ref": "string", "label": "string"},
        "output_schema": {"applied_count": "integer"},
        "risk_level": "WRITE",
    },
    "google.sheets.append_rows": {
        "name": "google.sheets.append_rows",
        "description": "Append rows to a Google Sheet",
        "input_schema": {"spreadsheet_id": "string", "sheet_name": "string", "rows_ref": "string"},
        "output_schema": {"rows_appended": "integer"},
        "risk_level": "WRITE",
    },
    "stripe.payments.list": {
        "name": "stripe.payments.list",
        "description": "List Stripe payments for a date range",
        "input_schema": {"start_date": "string", "end_date": "string"},
        "output_schema": {"payments": "array"},
        "risk_level": "READ",
    },
    "slack.chat.postMessage": {
        "name": "slack.chat.postMessage",
        "description": "Post a message to a Slack channel",
        "input_schema": {"channel": "string", "text": "string"},
        "output_schema": {"ts": "string", "channel": "string"},
        "risk_level": "WRITE",
    },
    "taskpilot.llm.summarize": {
        "name": "taskpilot.llm.summarize",
        "description": "Summarize items using LLM",
        "input_schema": {"items_ref": "string", "style": "string"},
        "output_schema": {"summary": "string"},
        "risk_level": "READ",
    },
    "taskpilot.llm.draft_emails": {
        "name": "taskpilot.llm.draft_emails",
        "description": "Draft emails using LLM",
        "input_schema": {"messages_ref": "string", "tone": "string", "ask": "string"},
        "output_schema": {"drafts": "array"},
        "risk_level": "READ",
    },
    "taskpilot.data.aggregate": {
        "name": "taskpilot.data.aggregate",
        "description": "Aggregate data by grouping and summing",
        "input_schema": {"input_ref": "string", "group_by": "array", "sum": "array"},
        "output_schema": {"rows": "array"},
        "risk_level": "READ",
    },
    "taskpilot.report.pdf": {
        "name": "taskpilot.report.pdf",
        "description": "Generate a PDF report",
        "input_schema": {"template": "string", "data_ref": "string", "title": "string"},
        "output_schema": {"file": "string"},
        "risk_level": "READ",
    },
}


def get_all_tools() -> list[dict]:
    return list(TOOLS.values())


def get_tool(name: str) -> dict | None:
    return TOOLS.get(name)


def validate_tool_exists(name: str) -> bool:
    return name in TOOLS
