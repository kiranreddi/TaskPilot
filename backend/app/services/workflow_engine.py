"""Workflow execution engine."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models
from app.services.tool_registry import get_tool, validate_tool_exists
from app.services.approval_engine import validate_approval


def validate_definition(definition: dict) -> tuple[bool, str | None]:
    """Validate a workflow definition against expected schema."""
    if not isinstance(definition, dict):
        return False, "Definition must be a dict"

    steps = definition.get("steps")
    if not steps or not isinstance(steps, list):
        return False, "Definition must contain a 'steps' list"

    for i, step in enumerate(steps):
        if "id" not in step:
            return False, f"Step {i} missing 'id'"
        if "tool" not in step:
            return False, f"Step {i} missing 'tool'"
        if not validate_tool_exists(step["tool"]):
            return False, f"Step {i} references unknown tool '{step['tool']}'"

    return True, None


def execute_workflow(
    db: Session,
    run: models.Run,
    definition: dict,
    require_approval_for_write: bool,
    approval_token: str | None = None,
) -> models.Run:
    """Execute a workflow run by processing steps sequentially."""
    steps = definition.get("steps", [])

    # Check approval
    approved, err = validate_approval(steps, require_approval_for_write, approval_token)
    if not approved:
        run.status = "FAILED"
        run.output_summary = err
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
        return run

    run.status = "RUNNING"
    run.started_at = datetime.now(timezone.utc)
    db.commit()

    for i, step_def in enumerate(steps):
        run_step = models.RunStep(
            run_id=run.id,
            step_index=i,
            tool=step_def["tool"],
            status="RUNNING",
            input_json=step_def.get("args", {}),
            started_at=datetime.now(timezone.utc),
        )
        db.add(run_step)
        db.commit()

        # Reload run to check for cancellation
        db.refresh(run)
        if run.status == "CANCELED":
            run_step.status = "CANCELED"
            run_step.finished_at = datetime.now(timezone.utc)
            db.commit()
            break

        # Simulate tool execution
        tool = get_tool(step_def["tool"])
        run_step.output_json = {"result": f"Simulated output from {tool['name']}"}
        run_step.status = "SUCCEEDED"
        run_step.finished_at = datetime.now(timezone.utc)
        db.commit()

    # Finalize run
    db.refresh(run)
    if run.status != "CANCELED":
        run.status = "SUCCEEDED"
        run.output_summary = f"Completed {len(steps)} steps successfully"
    run.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run
