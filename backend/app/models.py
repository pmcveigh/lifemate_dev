from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.ticket import TicketStatus
from app.models.user import User, UserRole  # noqa: F401

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
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="ticket", cascade="all, delete-orphan")
    assignee = relationship("User", back_populates="assigned_tickets")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    author = Column(String(100), nullable=True)
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ticket = relationship("Ticket", back_populates="comments")
    author_user = relationship(
        "User",
        back_populates="comments",
        foreign_keys="Comment.author_id",
    )

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    eta = Column(DateTime, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    created_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ticket = relationship("Ticket", back_populates="tasks")
    created_by = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys="Task.created_by_id",
    )

