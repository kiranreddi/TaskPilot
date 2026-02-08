from app.services.workflow_engine import validate_definition, execute_workflow
from app.services.tool_registry import get_all_tools, get_tool, validate_tool_exists
from app.services.approval_engine import step_requires_approval, validate_approval
from app import models


def test_validate_definition_valid():
    defn = {
        "steps": [
            {"id": "s1", "tool": "taskpilot.llm.summarize", "args": {}}
        ]
    }
    valid, err = validate_definition(defn)
    assert valid is True
    assert err is None


def test_validate_definition_missing_steps():
    valid, err = validate_definition({})
    assert valid is False
    assert "steps" in err


def test_validate_definition_unknown_tool():
    defn = {
        "steps": [{"id": "s1", "tool": "unknown.tool"}]
    }
    valid, err = validate_definition(defn)
    assert valid is False
    assert "unknown" in err


def test_validate_definition_missing_id():
    defn = {
        "steps": [{"tool": "taskpilot.llm.summarize"}]
    }
    valid, err = validate_definition(defn)
    assert valid is False
    assert "id" in err


def test_validate_definition_missing_tool():
    defn = {
        "steps": [{"id": "s1"}]
    }
    valid, err = validate_definition(defn)
    assert valid is False
    assert "tool" in err


def test_get_all_tools():
    tools = get_all_tools()
    assert len(tools) == 9
    names = [t["name"] for t in tools]
    assert "google.gmail.search" in names
    assert "taskpilot.report.pdf" in names


def test_get_tool_exists():
    tool = get_tool("google.gmail.search")
    assert tool is not None
    assert tool["risk_level"] == "READ"


def test_get_tool_not_exists():
    assert get_tool("nonexistent") is None


def test_validate_tool_exists():
    assert validate_tool_exists("google.gmail.search") is True
    assert validate_tool_exists("nonexistent") is False


def test_step_requires_approval_write():
    assert step_requires_approval("google.gmail.label.apply", True) is True
    assert step_requires_approval("google.gmail.label.apply", False) is False


def test_step_requires_approval_read():
    assert step_requires_approval("google.gmail.search", True) is False


def test_validate_approval_no_write_steps():
    steps = [{"tool": "google.gmail.search"}]
    approved, err = validate_approval(steps, True, None)
    assert approved is True


def test_validate_approval_write_steps_no_token():
    steps = [{"tool": "google.gmail.label.apply"}]
    approved, err = validate_approval(steps, True, None)
    assert approved is False
    assert "approval" in err.lower()


def test_validate_approval_write_steps_with_token():
    steps = [{"tool": "google.gmail.label.apply"}]
    approved, err = validate_approval(steps, True, "approved")
    assert approved is True


def test_execute_workflow(db_session):
    user = models.User(id="eng-user", email="eng@test.com", name="Eng", password_hash="x")
    db_session.add(user)
    db_session.flush()

    org = models.Org(id="eng-org", name="Eng Org", owner_user_id=user.id)
    db_session.add(org)
    db_session.flush()

    wf = models.Workflow(id="eng-wf", org_id=org.id, name="Test", created_by=user.id)
    db_session.add(wf)
    db_session.flush()

    version = models.WorkflowVersion(
        id="eng-wfv",
        workflow_id=wf.id,
        version=1,
        definition_json={
            "steps": [
                {"id": "s1", "tool": "taskpilot.llm.summarize", "args": {"items_ref": "input", "style": "default"}}
            ]
        },
    )
    db_session.add(version)
    db_session.flush()

    run = models.Run(
        id="eng-run",
        workflow_version_id=version.id,
        org_id=org.id,
        initiated_by=user.id,
    )
    db_session.add(run)
    db_session.commit()

    result = execute_workflow(
        db=db_session,
        run=run,
        definition=version.definition_json,
        require_approval_for_write=False,
    )
    assert result.status == "SUCCEEDED"
    assert len(result.steps) == 1
    assert result.steps[0].status == "SUCCEEDED"
