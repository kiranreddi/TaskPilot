from fastapi import APIRouter, Depends

from app import schemas
from app.deps import get_current_user

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return schemas.UserResponse(
        id=current_user["user_id"],
        email=current_user["email"],
        name=current_user["name"],
        org_id=current_user.get("org_id"),
        role=current_user.get("role"),
    )
