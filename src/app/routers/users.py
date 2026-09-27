from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserRoleUpdate

router = APIRouter(prefix="/users",tags=["users"])
@router.get("/",response_model = list[UserRead])
def fetch_users(db : Session = Depends(get_db)):  # noqa: B008
    stmt = select(User).order_by(User.created_at.desc())
    users = db.execute(stmt).scalars().all()
    return users


@router.patch("/role", response_model=UserRead)
def update_user_role(payload: UserRoleUpdate, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with email {payload.email}",
        )

    user.role = payload.role  # normalized to uppercase by the model validator
    db.commit()
    db.refresh(user)

    return user