import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user, get_db
from app.models.task import Tag, Task, TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import (
    PaginatedTasks,
    TaskCreate,
    TaskDetail,
    TaskMove,
    TaskRead,
    TaskUpdate,
)

router = APIRouter(tags=["tasks"])


@router.get("/projects/{project_id}/tasks", response_model=PaginatedTasks)
def list_tasks(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    status_filter: TaskStatus | None = Query(None, alias="status"),
    priority: TaskPriority | None = None,
    assignee: uuid.UUID | None = None,
    tag: uuid.UUID | None = None,
    due_before: datetime | None = None,
    q: str | None = Query(None, description="Search in title/description"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: Literal["created_at", "due_date", "priority", "position"] = "position",
    sort_order: Literal["asc", "desc"] = "asc",
):
    stmt = select(Task).where(Task.project_id == project_id)
    count_stmt = select(func.count()).select_from(Task).where(Task.project_id == project_id)

    if status_filter:
        stmt = stmt.where(Task.status == status_filter)
        count_stmt = count_stmt.where(Task.status == status_filter)
    if priority:
        stmt = stmt.where(Task.priority == priority)
        count_stmt = count_stmt.where(Task.priority == priority)
    if assignee:
        stmt = stmt.where(Task.assignee_id == assignee)
        count_stmt = count_stmt.where(Task.assignee_id == assignee)
    if due_before:
        stmt = stmt.where(Task.due_date <= due_before)
        count_stmt = count_stmt.where(Task.due_date <= due_before)
    if q:
        search = Task.title.ilike(f"%{q}%") | Task.description.ilike(f"%{q}%")
        stmt = stmt.where(search)
        count_stmt = count_stmt.where(search)
    if tag:
        stmt = stmt.join(Task.tags).where(Tag.id == tag)
        count_stmt = count_stmt.join(Task.tags).where(Tag.id == tag)

    total = db.execute(count_stmt).scalar_one()

    sort_column = getattr(Task, sort_by)
    stmt = stmt.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())
    stmt = stmt.options(selectinload(Task.tags)).offset((page - 1) * size).limit(size)

    tasks = db.execute(stmt).scalars().all()
    return PaginatedTasks(items=tasks, total=total, page=page, size=size)


@router.post("/projects/{project_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: uuid.UUID,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(
        project_id=project_id,
        created_by=current_user.id,
        **payload.model_dump(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=TaskDetail)
def get_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    stmt = (
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.tags), selectinload(Task.subtasks))
    )
    task = db.execute(stmt).scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: uuid.UUID, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/move", response_model=TaskRead)
def move_task(task_id: uuid.UUID, payload: TaskMove, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = payload.status
    task.position = payload.position
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


@router.get("/tasks/mytask/me", response_model=list[TaskRead])
def my_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    print(current_user.id)
    stmt = (
        select(Task)
        .where(Task.assignee_id == current_user.id)
        .options(selectinload(Task.tags))
        .order_by(Task.due_date.asc().nulls_last())
    )
    return db.execute(stmt).scalars().all()