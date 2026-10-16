


import uuid
from operator import or_
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.schemas.project import (
    MemberInvite,
    MemberRead,
    MemberRoleUpdate,
    MemberWithUserRead,
    PaginatedProjects,
    ProjectCreate,
    ProjectOwnerUpdate,
    ProjectRead,
    ProjectWithUserRead,
)
from app.schemas.user import MessageResponse

router = APIRouter(prefix="/project",tags=["project"])

@router.post("/create",response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def register_Project(payload:ProjectCreate, db:Session= Depends(get_db)):
    existing = db.execute(
        Select(Project).where(Project.name == payload.name)
        ).scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail="A Project with the same name already exist",
        )

    projectDet = Project(
        owner_id = payload.owner_id,
        name = payload.name,
        description = payload.description
    )
    # try:
    db.add(projectDet)
    db.commit()
    db.refresh(projectDet)
    # except IntegrityError:
    #     db.rollback()
    #     raise HTTPException(status_code=400, detail="Invalid owner_id or constraint violation")

    return projectDet

@router.get("",response_model = PaginatedProjects)
def fetch_rolebasedUsers(db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search by email or full name"),
    sort_by: Literal["email", "full_name", "created_at"] = Query("created_at"),
    sort_order: Literal["asc", "desc"] = Query("desc")): 
    stmt = (
        Select(Project)
    )
    count_stmt = select(func.count()).select_from(Project)
       
    if search:
        search_filter = or_(
            Project.owner_id.ilike(f"%{search}%"),
            Project.name.ilike(f"%{search}%"),
        )
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)

    sort_column = getattr(Project, sort_by)
    stmt = stmt.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())

    total = db.execute(count_stmt).scalar_one()

    stmt = stmt.offset((page - 1) * size).limit(size)
    users = db.execute(stmt).scalars().all()

    return PaginatedProjects(items=users, total=total, page=page, size=size)

@router.patch("/updateOwner/{project_id}",response_model=ProjectRead)
def update_ownerDetails(project_id:uuid.UUID,payload:ProjectOwnerUpdate,db:Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project Not Found")
    checkUser = db.get(User,payload.user_id)
    if checkUser is None:
        raise HTTPException(status_code=404,detail="User Not Found. Check User again")
    
    print(checkUser,project,"PROJECT")
    projectupdate = db.execute(Select(Project).where(Project.id == project_id)).scalar_one_or_none()

    projectupdate.owner_id = payload.user_id
    db.commit()
    db.refresh(projectupdate)
    return projectupdate
def _get_project_or_404(db: Session, project_id: uuid.UUID) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

def _get_project_or_405(db: Session, project_id: uuid.UUID) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    stmt = (
        select(
            Project.id,
            Project.owner_id,
            Project.name,
            Project.description,
            Project.created_at,
            User.id,
            User.full_name,
        )
        .join(User, User.id == Project.owner_id)
        .where(Project.id == project_id)
    )

    rows = db.execute(stmt).all()

    return [
        ProjectWithUserRead(
            id = row.id,
            owner_id = row.owner_id,
            name = row.name,
            created_at= row.created_at,
            description = row.description,
            full_name = row.full_name
        )
        for row in rows
    ]


def _get_membership(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> ProjectMember | None:
    return db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    ).scalar_one_or_none()


@router.get("/{project_id}", response_model=list[ProjectWithUserRead])
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    return _get_project_or_405(db, project_id)


@router.delete("/{project_id}", response_model=MessageResponse)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id)

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can delete this project",
        )

    db.delete(project)
    db.commit()
    return MessageResponse(message=f"Project '{project.name}' deleted successfully")


@router.get("/{project_id}/members", response_model=list[MemberWithUserRead])
def list_members(project_id: uuid.UUID, db: Session = Depends(get_db)):
    # _get_project_or_404(db, project_id)
    # stmt = select(ProjectMember).where(ProjectMember.project_id == project_id)
    # return db.execute(stmt).scalars().all()
    _get_project_or_404(db, project_id)

    stmt = (
        select(
            ProjectMember.user_id,
            ProjectMember.role,
            ProjectMember.joined_at,
            User.email,
            User.full_name,
        )
        .join(User, User.id == ProjectMember.user_id)
        .where(ProjectMember.project_id == project_id)
    )

    rows = db.execute(stmt).all()

    return [
        MemberWithUserRead(
            user_id=row.user_id,
            role=row.role,
            joined_at=row.joined_at,
            email=row.email,
            full_name=row.full_name,
        )
        for row in rows
    ]

@router.post("/{project_id}/members", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def invite_member(
    project_id: uuid.UUID,
    payload: MemberInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id)

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can invite members")

    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    existing = _get_membership(db, project_id, payload.user_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="User is already a member of this project")

    membership = ProjectMember(
        project_id=project_id,
        user_id=payload.user_id,
        role=payload.role,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


@router.patch("/{project_id}/members/{user_id}", response_model=MemberRead)
def change_member_role(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: MemberRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id)

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can change member roles")

    membership = _get_membership(db, project_id, user_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="This user is not a member of the project")

    membership.role = payload.role
    db.commit()
    db.refresh(membership)
    return membership


@router.delete("/{project_id}/members/{user_id}", response_model=MessageResponse)
def remove_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(db, project_id)

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the project owner can remove members")

    if user_id == project.owner_id:
        raise HTTPException(status_code=400, detail="The project owner cannot be removed")

    membership = _get_membership(db, project_id, user_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="This user is not a member of the project")

    db.delete(membership)
    db.commit()
    return MessageResponse(message="Member removed successfully")