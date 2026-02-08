from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import hash_password, verify_password, create_access_token
from app.deps import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(req: schemas.SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = models.User(email=req.email, name=req.name, password_hash=hash_password(req.password))
    db.add(user)
    db.flush()

    # Create default org
    org = models.Org(name=f"{req.name}'s Org", owner_user_id=user.id)
    db.add(org)
    db.flush()

    membership = models.Membership(user_id=user.id, org_id=org.id, role="OWNER")
    db.add(membership)
    db.commit()

    token = create_access_token({"user_id": user.id, "org_id": org.id, "role": "OWNER"})
    return schemas.TokenResponse(access_token=token)


@router.post("/login", response_model=schemas.TokenResponse)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    membership = db.query(models.Membership).filter(models.Membership.user_id == user.id).first()
    org_id = membership.org_id if membership else None
    role = membership.role if membership else None

    token = create_access_token({"user_id": user.id, "org_id": org_id, "role": role})
    return schemas.TokenResponse(access_token=token)
