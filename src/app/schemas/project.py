
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    owner_id: uuid.UUID
    name: str
    description: str

class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    created_at: datetime

class ProjectGetMembers(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id : uuid.UUID
    user_id: uuid.UUID
    role: str
    joined_at: datetime

class createProjectMem(BaseModel):
    project_id : uuid.UUID
    user_id: uuid.UUID
    role : str