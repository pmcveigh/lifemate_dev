from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

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

class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TicketStatus = TicketStatus.todo
    category: Optional[str] = None
    room: Optional[str] = None
    assignee: Optional[str] = None

class TicketCreate(TicketBase):
    comments: List[CommentCreate] = []
    tasks: List[TaskCreate] = []

class TicketRead(TicketBase):
    id: int
    position: int
    comments: List[CommentRead] = []
    tasks: List[TaskRead] = []
    created_at: datetime
    updated_at: datetime

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    category: Optional[str] = None
    room: Optional[str] = None
    assignee: Optional[str] = None
    position: Optional[int] = None

