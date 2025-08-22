from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    todo = "todo"
    inprogress = "inprogress"
    review = "review"
    completed = "completed"

class TaskBase(BaseModel):
    head: str
    description: str | None = None
    status: Optional[TaskStatus] = TaskStatus.todo
    team_id: Optional[int] = None
    assigned_to: Optional[int] = None
    reporter: Optional[int] = None
    created_at: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskOut(TaskBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class PaginatedTaskOut(BaseModel):
    total: int
    items: List[TaskOut]