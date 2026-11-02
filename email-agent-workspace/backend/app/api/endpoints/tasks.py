"""
API Endpoints for Task Management (To-Do Items).
Provides full CRUD capabilities for action items persisted in MSSQL.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.db.models import TaskModel
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

router = APIRouter()

@router.get("", response_model=TaskListResponse)
def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status: pending, in_progress, completed"),
    urgency: Optional[str] = Query(None, description="Filter by urgency: low, medium, high, urgent"),
    email_id: Optional[int] = Query(None, description="Filter by associated email ID"),
    db: Session = Depends(get_db)
):
    """Lists all tasks with optional status and urgency filters."""
    query = db.query(TaskModel)
    if status:
        query = query.filter(TaskModel.status == status)
    if urgency:
        query = query.filter(TaskModel.urgency == urgency)
    if email_id:
        query = query.filter(TaskModel.email_id == email_id)

    total = query.count()
    tasks = query.order_by(TaskModel.created_at.desc()).all()
    return TaskListResponse(total=total, tasks=tasks)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    """Creates a new task record in MSSQL."""
    task = TaskModel(
        email_id=task_in.email_id,
        title=task_in.title,
        description=task_in.description,
        owner=task_in.owner,
        due_date=task_in.due_date,
        urgency=task_in.urgency,
        status=task_in.status
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Fetches a specific task by ID."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    """Updates an existing task."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(task, field, val)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Deletes a task from MSSQL."""
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None
