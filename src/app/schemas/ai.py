import uuid
from datetime import date

from pydantic import BaseModel

from app.models.task import TaskPriority


class ParseTaskRequest(BaseModel):
    project_id: uuid.UUID
    text: str


class ParseTaskResponse(BaseModel):
    title: str
    priority: TaskPriority
    due_date: date | None