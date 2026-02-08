"""Approval policy enforcement."""

from app.services.tool_registry import get_tool


def step_requires_approval(tool_name: str, require_approval_for_write: bool) -> bool:
    """Check if a step requires approval based on tool risk and org policy."""
    tool = get_tool(tool_name)
    if tool is None:
        return False
    return tool["risk_level"] == "WRITE" and require_approval_for_write


def validate_approval(
    steps: list[dict],
    require_approval_for_write: bool,
    approval_token: str | None,
) -> tuple[bool, str | None]:
    """
    Validate that approval is granted for all WRITE steps if policy requires it.
    Returns (approved, error_message).
    """
    has_write_steps = any(
        step_requires_approval(step.get("tool", ""), require_approval_for_write)
        for step in steps
    )

    if has_write_steps and not approval_token:
        return False, "Workflow contains WRITE steps that require approval. Provide an approval_token."

    return True, None
