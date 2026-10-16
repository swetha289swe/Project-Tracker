
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.project import MemberRole
from app.schemas.common import Pagination


class ProjectCreate(BaseModel):
    owner_id: uuid.UUID
    name: str
    description: str

class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    created_at: datetime

class PaginatedProjects(Pagination[ProjectRead]):
    pass

class ProjectOwnerUpdate(BaseModel):
    user_id: uuid.UUID

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

class MemberInvite(BaseModel):
    user_id: uuid.UUID
    role: MemberRole = MemberRole.viewer


class MemberRoleUpdate(BaseModel):
    role: MemberRole


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    role: MemberRole
    joined_at: datetime


class MessageResponse(BaseModel):
    message: str

class MemberWithUserRead(BaseModel):
    user_id: uuid.UUID
    role: MemberRole
    joined_at: datetime
    email: str
    full_name: str

class ProjectWithUserRead(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    created_at: datetime
    description: str
    full_name: str