from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# Auth
class SignupRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# User
class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    org_id: Optional[str] = None
    role: Optional[str] = None

    model_config = {"from_attributes": True}


# Connections
class ConnectionResponse(BaseModel):
    id: str
    org_id: str
    provider: str
    status: str
    scopes: Optional[list] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OAuthStartResponse(BaseModel):
    authorize_url: str
    connection_id: str


# Integrations
class IntegrationResponse(BaseModel):
    provider: str
    name: str
    description: str
    auth_type: str


# Workflows
class WorkflowCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: Optional[str] = None
    template_id: Optional[str] = None
    definition: Optional[dict] = None


class WorkflowResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    status: str
    created_by: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class WorkflowRunRequest(BaseModel):
    inputs: Optional[dict] = None
    approval_token: Optional[str] = None


# Runs
class RunStepResponse(BaseModel):
    id: str
    step_index: int
    tool: str
    status: str
    input_json: Optional[dict] = None
    output_json: Optional[dict] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RunResponse(BaseModel):
    id: str
    workflow_version_id: str
    org_id: str
    status: str
    initiated_by: str
    input_json: Optional[dict] = None
    output_summary: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    steps: Optional[list[RunStepResponse]] = None

    model_config = {"from_attributes": True}


# Templates
class TemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    tags: list[str]
    definition: dict


# Billing
class BillingWebhookResponse(BaseModel):
    received: bool


# Admin
class MemberResponse(BaseModel):
    id: str
    user_id: str
    org_id: str
    role: str
    email: Optional[str] = None
    name: Optional[str] = None

    model_config = {"from_attributes": True}


class InviteMemberRequest(BaseModel):
    email: str
    role: str = "MEMBER"


class PolicyResponse(BaseModel):
    require_approval_for_write: bool


class PolicyUpdateRequest(BaseModel):
    require_approval_for_write: bool
