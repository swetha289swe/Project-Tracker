

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectRead

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