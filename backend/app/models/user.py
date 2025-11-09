from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, Enum):
    global_admin = "global_admin"
    home_admin = "home_admin"
    home_user = "home_user"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username", name="uq_users_username"),)

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole, name="userrole"), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    assigned_tickets = relationship(
        "Ticket",
        back_populates="assignee",
        foreign_keys="Ticket.assignee_id",
    )
    comments = relationship(
        "Comment",
        back_populates="author_user",
        foreign_keys="Comment.author_id",
    )
    created_tasks = relationship(
        "Task",
        back_populates="created_by",
        foreign_keys="Task.created_by_id",
    )
