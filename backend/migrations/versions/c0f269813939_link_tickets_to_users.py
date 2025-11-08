"""Link tickets to users via assignee_id."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c0f269813939"
down_revision: Union[str, Sequence[str], None] = "9b54f0f2e4b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column("assignee_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_tickets_assignee_id"), "tickets", ["assignee_id"], unique=False
    )
    op.create_foreign_key(
        "fk_tickets_assignee_id_users",
        "tickets",
        "users",
        ["assignee_id"],
        ["id"],
        ondelete="SET NULL",
    )

    tickets = sa.table(
        "tickets",
        sa.column("id", sa.Integer()),
        sa.column("assignee", sa.String()),
        sa.column("assignee_id", sa.Integer()),
    )
    users = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("username", sa.String()),
    )

    bind = op.get_bind()
    user_rows = bind.execute(sa.select(users.c.username, users.c.id)).all()
    username_to_id = {row.username: row.id for row in user_rows}

    if username_to_id:
        ticket_rows = bind.execute(sa.select(tickets.c.id, tickets.c.assignee)).all()
        for ticket_id, assignee_name in ticket_rows:
            if assignee_name:
                user_id = username_to_id.get(assignee_name)
                if user_id:
                    bind.execute(
                        sa.update(tickets)
                        .where(tickets.c.id == ticket_id)
                        .values(assignee_id=user_id)
                    )

    op.drop_column("tickets", "assignee")


def downgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column("assignee", sa.String(length=100), nullable=True),
    )

    tickets = sa.table(
        "tickets",
        sa.column("id", sa.Integer()),
        sa.column("assignee", sa.String()),
        sa.column("assignee_id", sa.Integer()),
    )
    users = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("username", sa.String()),
    )

    bind = op.get_bind()
    user_rows = bind.execute(sa.select(users.c.id, users.c.username)).all()
    user_id_to_username = {row.id: row.username for row in user_rows}

    ticket_rows = bind.execute(sa.select(tickets.c.id, tickets.c.assignee_id)).all()
    for ticket_id, assignee_id in ticket_rows:
        if assignee_id is not None:
            username = user_id_to_username.get(assignee_id)
            if username:
                bind.execute(
                    sa.update(tickets)
                    .where(tickets.c.id == ticket_id)
                    .values(assignee=username)
                )

    op.drop_constraint("fk_tickets_assignee_id_users", "tickets", type_="foreignkey")
    op.drop_index(op.f("ix_tickets_assignee_id"), table_name="tickets")
    op.drop_column("tickets", "assignee_id")
