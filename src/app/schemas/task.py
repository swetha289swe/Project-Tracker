import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.medium
    assignee_id: uuid.UUID | None = None
    due_date: datetime | None = None
    parent_task_id: uuid.UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: uuid.UUID | None = None
    due_date: datetime | None = None


class TaskMove(BaseModel):
    status: TaskStatus
    position: int


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    color: str | None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    parent_task_id: uuid.UUID | None
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assignee_id: uuid.UUID | None
    created_by: uuid.UUID
    due_date: datetime | None
    position: int
    created_at: datetime
    tags: list[TagRead] = []


class TaskDetail(TaskRead):
    subtasks: list[TaskRead] = []


class PaginatedTasks(BaseModel):
    items: list[TaskRead]
    total: int
    page: int
    size: int