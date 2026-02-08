import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Integer, Text, Boolean, JSON, Index
)
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    memberships = relationship("Membership", back_populates="user")


class Org(Base):
    __tablename__ = "orgs"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    owner_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    require_approval_for_write = Column(Boolean, default=True)

    memberships = relationship("Membership", back_populates="org")
    connections = relationship("Connection", back_populates="org")
    workflows = relationship("Workflow", back_populates="org")


class Membership(Base):
    __tablename__ = "memberships"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    org_id = Column(String, ForeignKey("orgs.id"), nullable=False)
    role = Column(String, nullable=False, default="MEMBER")  # OWNER/ADMIN/MEMBER/VIEWER
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="memberships")
    org = relationship("Org", back_populates="memberships")

    __table_args__ = (
        Index("ix_memberships_org_user", "org_id", "user_id"),
    )


class Connection(Base):
    __tablename__ = "connections"
    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("orgs.id"), nullable=False)
    provider = Column(String, nullable=False)
    status = Column(String, nullable=False, default="CONNECTED")
    scopes = Column(JSON, default=list)
    token_ciphertext = Column(Text, nullable=True)
    last_ok_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    org = relationship("Org", back_populates="connections")

    __table_args__ = (
        Index("ix_connections_org_provider", "org_id", "provider"),
    )


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("orgs.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="ACTIVE")
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)

    org = relationship("Org", back_populates="workflows")
    versions = relationship("WorkflowVersion", back_populates="workflow")


class WorkflowVersion(Base):
    __tablename__ = "workflow_versions"
    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    definition_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    workflow = relationship("Workflow", back_populates="versions")


class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    cron = Column(String, nullable=False)
    timezone = Column(String, nullable=False, default="UTC")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class Run(Base):
    __tablename__ = "runs"
    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_version_id = Column(String, ForeignKey("workflow_versions.id"), nullable=False)
    org_id = Column(String, ForeignKey("orgs.id"), nullable=False)
    status = Column(String, nullable=False, default="QUEUED")
    initiated_by = Column(String, ForeignKey("users.id"), nullable=False)
    input_json = Column(JSON, nullable=True)
    output_summary = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    steps = relationship("RunStep", back_populates="run")
    workflow_version = relationship("WorkflowVersion")

    __table_args__ = (
        Index("ix_runs_wv_started", "workflow_version_id", "started_at"),
    )


class RunStep(Base):
    __tablename__ = "run_steps"
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    step_index = Column(Integer, nullable=False)
    tool = Column(String, nullable=False)
    status = Column(String, nullable=False, default="QUEUED")
    input_json = Column(JSON, nullable=True)
    output_json = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    run = relationship("Run", back_populates="steps")

    __table_args__ = (
        Index("ix_run_steps_run_step", "run_id", "step_index"),
    )


class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(String, primary_key=True, default=generate_uuid)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    type = Column(String, nullable=False)
    storage_url = Column(String, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class UsageEvent(Base):
    __tablename__ = "usage_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("orgs.id"), nullable=False)
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    tool_calls = Column(Integer, default=0)
    timestamp = Column(DateTime, default=utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("orgs.id"), nullable=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    plan = Column(String, nullable=False, default="free")
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=utcnow)
