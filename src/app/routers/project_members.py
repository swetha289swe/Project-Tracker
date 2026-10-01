from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.project import ProjectMember
from app.schemas.project import ProjectGetMembers, createProjectMem

router = APIRouter(prefix="/pro-members",tags=["pro-members"])

@router.get("/",response_model=list[ProjectGetMembers])
def get_ProjectMembers(db:Session=Depends(get_db)):
    stmts = Select(ProjectMember).order_by(ProjectMember.joined_at.desc())
    exe = db.execute(stmts).scalars().all()
    return exe


@router.post("/create",response_model=ProjectGetMembers, status_code=status.HTTP_201_CREATED)
def register_Project(payload:createProjectMem, db:Session= Depends(get_db)):
    existing = db.execute(
        Select(ProjectMember).where(ProjectMember.user_id == payload.user_id and ProjectMember.project_id == payload.project_id)
        ).scalar_one_or_none()
    print("EXISTING",existing)
    if existing is not None:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail="A Project with the same name already exist",
        )

    projectDet = ProjectMember(
        project_id = payload.project_id,
        user_id = payload.user_id,
        role = payload.role
    )
    db.add(projectDet)
    db.commit()
    db.refresh(projectDet)
  
    return projectDet