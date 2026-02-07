from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import hash_password, create_access_token
from app.deps import get_db, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/members", response_model=list[schemas.MemberResponse])
def list_members(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    org_id = current_user["org_id"]
    memberships = db.query(models.Membership).filter(models.Membership.org_id == org_id).all()
    result = []
    for m in memberships:
        user = db.query(models.User).filter(models.User.id == m.user_id).first()
        result.append(schemas.MemberResponse(
            id=m.id,
            user_id=m.user_id,
            org_id=m.org_id,
            role=m.role,
            email=user.email if user else None,
            name=user.name if user else None,
        ))
    return result


@router.post("/members/invite", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED)
def invite_member(
    req: schemas.InviteMemberRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    org_id = current_user["org_id"]

    # Check if user already exists
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        user = models.User(email=req.email, name=req.email.split("@")[0], password_hash=hash_password("changeme"))
        db.add(user)
        db.flush()

    existing = db.query(models.Membership).filter(
        models.Membership.user_id == user.id,
        models.Membership.org_id == org_id,
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already a member")

    membership = models.Membership(user_id=user.id, org_id=org_id, role=req.role)
    db.add(membership)
    db.commit()
    db.refresh(membership)

    return schemas.MemberResponse(
        id=membership.id,
        user_id=membership.user_id,
        org_id=membership.org_id,
        role=membership.role,
        email=user.email,
        name=user.name,
    )


@router.get("/policies", response_model=schemas.PolicyResponse)
def get_policies(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    org = db.query(models.Org).filter(models.Org.id == current_user["org_id"]).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Org not found")
    return schemas.PolicyResponse(require_approval_for_write=org.require_approval_for_write)


@router.put("/policies", response_model=schemas.PolicyResponse)
def update_policies(
    req: schemas.PolicyUpdateRequest,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    org = db.query(models.Org).filter(models.Org.id == current_user["org_id"]).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Org not found")
    org.require_approval_for_write = req.require_approval_for_write
    db.commit()
    db.refresh(org)
    return schemas.PolicyResponse(require_approval_for_write=org.require_approval_for_write)
