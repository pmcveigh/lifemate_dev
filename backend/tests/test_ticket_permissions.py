import os
from typing import Optional

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.tickets import add_ticket_comment
from app.database import Base
from app.models import Ticket
from app.models.user import User, UserRole
from app.schemas.ticket import CommentCreate, TicketStatus


engine = create_engine(
    "sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _create_user(session, username: str, role: UserRole) -> User:
    user = User(username=username, role=role, hashed_password="not-used")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _create_ticket(session, assignee_id: Optional[int]) -> Ticket:
    ticket = Ticket(
        title="Test Ticket",
        description="",
        status=TicketStatus.todo,
        category=None,
        room=None,
        assignee_id=assignee_id,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


def test_home_user_can_comment_on_assigned_ticket(db_session):
    home_user = _create_user(db_session, "home", UserRole.home_user)
    ticket = _create_ticket(db_session, home_user.id)

    comment = add_ticket_comment(
        ticket.id,
        CommentCreate(author=home_user.username, text="My update"),
        db=db_session,
        current_user=home_user,
    )

    assert comment.text == "My update"
    assert comment.author == home_user.username


def test_home_user_denied_comment_on_unassigned_ticket(db_session):
    home_user = _create_user(db_session, "home", UserRole.home_user)
    other_user = _create_user(db_session, "other", UserRole.home_user)
    ticket = _create_ticket(db_session, other_user.id)

    with pytest.raises(HTTPException) as exc:
        add_ticket_comment(
            ticket.id,
            CommentCreate(author=home_user.username, text="Should fail"),
            db=db_session,
            current_user=home_user,
        )

    assert exc.value.status_code == 403


def test_manager_can_comment_on_any_ticket(db_session):
    manager = _create_user(db_session, "manager", UserRole.global_admin)
    other_user = _create_user(db_session, "other", UserRole.home_user)
    ticket = _create_ticket(db_session, other_user.id)

    comment = add_ticket_comment(
        ticket.id,
        CommentCreate(author=manager.username, text="Manager update"),
        db=db_session,
        current_user=manager,
    )

    assert comment.text == "Manager update"
