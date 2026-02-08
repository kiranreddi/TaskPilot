from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api", tags=["integrations"])

INTEGRATIONS_CATALOG = [
    {"provider": "google", "name": "Google Workspace", "description": "Gmail, Sheets, Drive, Calendar", "auth_type": "oauth2"},
    {"provider": "slack", "name": "Slack", "description": "Messaging and notifications", "auth_type": "oauth2"},
    {"provider": "stripe", "name": "Stripe", "description": "Payment processing and billing", "auth_type": "oauth2"},
    {"provider": "notion", "name": "Notion", "description": "Notes and documentation", "auth_type": "oauth2"},
    {"provider": "hubspot", "name": "HubSpot", "description": "CRM and marketing", "auth_type": "oauth2"},
]


@router.get("/integrations", response_model=list[schemas.IntegrationResponse])
def list_integrations():
    return [schemas.IntegrationResponse(**i) for i in INTEGRATIONS_CATALOG]


@router.get("/connections", response_model=list[schemas.ConnectionResponse])
def list_connections(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org_id = current_user["org_id"]
    connections = db.query(models.Connection).filter(models.Connection.org_id == org_id).all()
    return [schemas.ConnectionResponse.model_validate(c) for c in connections]


@router.post("/connections/{provider}/start", response_model=schemas.OAuthStartResponse)
def start_oauth(
    provider: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    valid_providers = [i["provider"] for i in INTEGRATIONS_CATALOG]
    if provider not in valid_providers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown provider: {provider}")

    connection = models.Connection(
        org_id=current_user["org_id"],
        provider=provider,
        status="CONNECTED",
        scopes=["read", "write"],
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)

    authorize_url = f"https://oauth.example.com/{provider}/authorize?connection_id={connection.id}"
    return schemas.OAuthStartResponse(authorize_url=authorize_url, connection_id=connection.id)
