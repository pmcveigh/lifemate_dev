from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.user import UserRole

class TicketStatus(str, Enum):
    backlog = "backlog"
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class CommentBase(BaseModel):
    author: Optional[str] = None
    text: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    author: Optional[str] = None
    text: Optional[str] = None

class CommentRead(CommentBase):
    id: int
    created_at: datetime
    author_id: Optional[int] = None

    model_config = {"from_attributes": True}

class TaskBase(BaseModel):
    text: str
    eta: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    text: Optional[str] = None
    eta: Optional[datetime] = None
    completed: Optional[bool] = None
    position: Optional[int] = None

class TaskRead(TaskBase):
    id: int
    completed: bool
    position: int
    created_by_id: Optional[int] = None

    model_config = {"from_attributes": True}


class TicketAssignee(BaseModel):
    id: int
    username: str
    role: UserRole

    model_config = {"from_attributes": True}

class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TicketStatus = TicketStatus.todo
    category: Optional[str] = None
    room: Optional[str] = None
    assignee_id: Optional[int] = None

class TicketCreate(TicketBase):
    comments: List[CommentCreate] = Field(default_factory=list)
    tasks: List[TaskCreate] = Field(default_factory=list)

class TicketRead(TicketBase):
    id: int
    position: int
    comments: List[CommentRead] = Field(default_factory=list)
    tasks: List[TaskRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    assignee: Optional[TicketAssignee] = None

    model_config = {"from_attributes": True}

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    category: Optional[str] = None
    room: Optional[str] = None
    assignee_id: Optional[int] = None
    position: Optional[int] = None
