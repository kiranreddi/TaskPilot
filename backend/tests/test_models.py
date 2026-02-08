"""Tests for SQLAlchemy ORM models."""
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app import models


def _make_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_user_model_creation():
    session = _make_session()
    user = models.User(id="u1", email="user@test.com", name="Test", password_hash="hashed")
    session.add(user)
    session.commit()
    fetched = session.query(models.User).filter_by(id="u1").first()
    assert fetched.email == "user@test.com"
    assert fetched.name == "Test"
    assert fetched.created_at is not None


def test_org_model_creation():
    session = _make_session()
    user = models.User(id="u1", email="org@test.com", name="Owner", password_hash="h")
    session.add(user)
    session.flush()
    org = models.Org(id="o1", name="My Org", owner_user_id="u1")
    session.add(org)
    session.commit()
    fetched = session.query(models.Org).filter_by(id="o1").first()
    assert fetched.name == "My Org"
    assert fetched.require_approval_for_write is True


def test_membership_creation_and_roles():
    session = _make_session()
    user = models.User(id="u1", email="m@test.com", name="M", password_hash="h")
    session.add(user)
    session.flush()
    org = models.Org(id="o1", name="Org", owner_user_id="u1")
    session.add(org)
    session.flush()

    for role in ("OWNER", "ADMIN", "MEMBER", "VIEWER"):
        mem = models.Membership(user_id="u1", org_id="o1", role=role)
        session.add(mem)
        session.flush()
        assert mem.role == role
    session.commit()
    count = session.query(models.Membership).filter_by(org_id="o1").count()
    assert count == 4


def test_connection_model_statuses():
    session = _make_session()
    user = models.User(id="u1", email="c@test.com", name="C", password_hash="h")
    session.add(user)
    session.flush()
    org = models.Org(id="o1", name="Org", owner_user_id="u1")
    session.add(org)
    session.flush()

    for st in ("CONNECTED", "DISCONNECTED", "ERROR"):
        conn = models.Connection(org_id="o1", provider="google", status=st)
        session.add(conn)
        session.flush()
        assert conn.status == st
    session.commit()


def test_workflow_model_statuses():
    session = _make_session()
    user = models.User(id="u1", email="w@test.com", name="W", password_hash="h")
    session.add(user)
    session.flush()
    org = models.Org(id="o1", name="Org", owner_user_id="u1")
    session.add(org)
    session.flush()

    wf_active = models.Workflow(id="wf1", org_id="o1", name="Active", status="ACTIVE", created_by="u1")
    wf_archived = models.Workflow(id="wf2", org_id="o1", name="Archived", status="ARCHIVED", created_by="u1")
    session.add_all([wf_active, wf_archived])
    session.commit()

    assert session.query(models.Workflow).filter_by(status="ACTIVE").count() == 1
    assert session.query(models.Workflow).filter_by(status="ARCHIVED").count() == 1


def test_workflow_version_definition_json():
    session = _make_session()
    user = models.User(id="u1", email="v@test.com", name="V", password_hash="h")
    session.add(user)
    session.flush()
    org = models.Org(id="o1", name="Org", owner_user_id="u1")
    session.add(org)
    session.flush()
    wf = models.Workflow(id="wf1", org_id="o1", name="WF", created_by="u1")
    session.add(wf)
    session.flush()

    definition = {"steps": [{"id": "s1", "tool": "test.tool"}]}
    ver = models.WorkflowVersion(workflow_id="wf1", version=1, definition_json=definition)
    session.add(ver)
    session.commit()
    session.refresh(ver)
    assert ver.definition_json == definition
    assert ver.version == 1


def test_run_model_state_transitions():
    session = _make_session()
    user = models.User(id="u1", email="r@test.com", name="R", password_hash="h")
    session.add(user)
    session.flush()
    org = models.Org(id="o1", name="Org", owner_user_id="u1")
    session.add(org)
    session.flush()
    wf = models.Workflow(id="wf1", org_id="o1", name="WF", created_by="u1")
    session.add(wf)
    session.flush()
    ver = models.WorkflowVersion(id="v1", workflow_id="wf1", version=1, definition_json={})
    session.add(ver)
    session.flush()

    run = models.Run(workflow_version_id="v1", org_id="o1", initiated_by="u1", status="QUEUED")
    session.add(run)
    session.commit()
    assert run.status == "QUEUED"

    run.status = "RUNNING"
    session.commit()
    assert run.status == "RUNNING"

    run.status = "SUCCEEDED"
    session.commit()
    assert run.status == "SUCCEEDED"


def test_run_step_model():
    session = _make_session()
    user = models.User(id="u1", email="rs@test.com", name="RS", password_hash="h")
    session.add(user)
    session.flush()
    org = models.Org(id="o1", name="Org", owner_user_id="u1")
    session.add(org)
    session.flush()
    wf = models.Workflow(id="wf1", org_id="o1", name="WF", created_by="u1")
    session.add(wf)
    session.flush()
    ver = models.WorkflowVersion(id="v1", workflow_id="wf1", version=1, definition_json={})
    session.add(ver)
    session.flush()
    run = models.Run(id="r1", workflow_version_id="v1", org_id="o1", initiated_by="u1")
    session.add(run)
    session.flush()

    step = models.RunStep(
        run_id="r1", step_index=0, tool="taskpilot.llm.summarize",
        status="SUCCEEDED", output_json={"result": "done"},
    )
    session.add(step)
    session.commit()
    fetched = session.query(models.RunStep).filter_by(run_id="r1").first()
    assert fetched.tool == "taskpilot.llm.summarize"
    assert fetched.output_json == {"result": "done"}


def test_artifact_model():
    session = _make_session()
    user = models.User(id="u1", email="a@test.com", name="A", password_hash="h")
    session.add(user)
    session.flush()
    org = models.Org(id="o1", name="Org", owner_user_id="u1")
    session.add(org)
    session.flush()
    wf = models.Workflow(id="wf1", org_id="o1", name="WF", created_by="u1")
    session.add(wf)
    session.flush()
    ver = models.WorkflowVersion(id="v1", workflow_id="wf1", version=1, definition_json={})
    session.add(ver)
    session.flush()
    run = models.Run(id="r1", workflow_version_id="v1", org_id="o1", initiated_by="u1")
    session.add(run)
    session.flush()

    artifact = models.Artifact(
        run_id="r1", type="report", storage_url="s3://bucket/report.pdf",
        metadata_json={"pages": 5},
    )
    session.add(artifact)
    session.commit()
    fetched = session.query(models.Artifact).filter_by(run_id="r1").first()
    assert fetched.type == "report"
    assert fetched.storage_url == "s3://bucket/report.pdf"
    assert fetched.metadata_json == {"pages": 5}


def test_usage_event_model():
    session = _make_session()
    user = models.User(id="u1", email="ue@test.com", name="UE", password_hash="h")
    session.add(user)
    session.flush()
    org = models.Org(id="o1", name="Org", owner_user_id="u1")
    session.add(org)
    session.flush()
    wf = models.Workflow(id="wf1", org_id="o1", name="WF", created_by="u1")
    session.add(wf)
    session.flush()
    ver = models.WorkflowVersion(id="v1", workflow_id="wf1", version=1, definition_json={})
    session.add(ver)
    session.flush()
    run = models.Run(id="r1", workflow_version_id="v1", org_id="o1", initiated_by="u1")
    session.add(run)
    session.flush()

    event = models.UsageEvent(
        org_id="o1", run_id="r1", tokens_in=100, tokens_out=50, tool_calls=3,
    )
    session.add(event)
    session.commit()
    fetched = session.query(models.UsageEvent).filter_by(run_id="r1").first()
    assert fetched.tokens_in == 100
    assert fetched.tokens_out == 50
    assert fetched.tool_calls == 3
    assert fetched.timestamp is not None
