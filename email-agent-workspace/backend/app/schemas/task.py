"""
Pydantic contracts for Task extraction, creation, and updating.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    title: str = Field(..., description="Actionable title of the task")
    description: Optional[str] = Field(default=None, description="Detailed instructions or context")
    owner: str = Field(default="Me", description="Assigned owner of the task")
    due_date: Optional[str] = Field(default=None, description="Extracted due date or timeframe")
    urgency: str = Field(default="medium", description="Urgency level: low, medium, high, urgent")
    status: str = Field(default="pending", description="Task status: pending, in_progress, completed")

class TaskCreate(TaskBase):
    email_id: Optional[int] = Field(default=None, description="Associated email reference ID")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[str] = None
    urgency: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    email_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class TaskListResponse(BaseModel):
    total: int
    tasks: List[TaskResponse]
