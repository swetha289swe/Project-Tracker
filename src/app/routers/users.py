import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.schemas.user import (
    UserbyName,
    UserListByRole,
    UserRead,
    UserRoleUpdate,
)

router = APIRouter(prefix="/users",tags=["users"])
@router.get("/",response_model = list[UserRead])
def fetch_users(db : Session = Depends(get_db)):  # noqa: B008
    stmt = select(User).order_by(User.created_at.desc())
    users = db.execute(stmt).scalars().all()
    return users

@router.get("/rolebasedList",response_model = list[UserListByRole])
def fetch_rolebasedUsers(name:str,db: Session = Depends(get_db)):  # noqa: B008
    print('NAME',name)
    stmts = (
        select(User)
        .where(User.role == name.upper())
        .order_by(User.created_at.desc())
    )
    usersByRole = db.execute(stmts).scalars().all()
    return usersByRole

@router.get("/userbyName",response_model = list[UserbyName])
def fetch_namebased(name:str,db: Session = Depends(get_db)):  # noqa: B008
    stmtname = (
        select(User)
        .where(User.full_name.ilike(f"%{name}%"))
    )
    usersByName = db.execute(stmtname).scalars().all()
    return usersByName

@router.patch("/role", response_model=UserRead)
def update_user_role(payload: UserRoleUpdate, db: Session = Depends(get_db)):  # noqa: B008
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

@router.delete("/{user_id}")
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    owned = db.execute(
        select(Project.name).where(Project.owner_id == user_id)
    ).scalars().all()

    member_of = db.execute(
        select(Project.name)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == user_id)
    ).scalars().all()

    blocking_projects = sorted(set(owned) | set(member_of))

    if blocking_projects:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"User cannot be deleted as they are associated with: "
                f"{', '.join(blocking_projects)}"
            ),
        )

    user_email = user.email  # capture before the row is gone
    db.delete(user)
    db.commit()

    return {"message": f"User '{user_email}' deleted successfully"}