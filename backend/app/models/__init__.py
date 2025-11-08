from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.schemas.ticket import TicketStatus


class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.todo)
    category = Column(String(100), nullable=True)
    room = Column(String(100), nullable=True)
    assignee_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    priority = Column(Integer, nullable=True)  # ← add it right here
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="ticket", cascade="all, delete-orphan")
    assignee = relationship("User", back_populates="assigned_tickets")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author = Column(String(100), nullable=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ticket = relationship("Ticket", back_populates="comments")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text = Column(Text, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    eta = Column(DateTime, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    ticket = relationship("Ticket", back_populates="tasks")


from .user import User, UserRole

__all__ = [
    "Ticket",
    "Comment",
    "Task",
    "User",
    "UserRole",
]

