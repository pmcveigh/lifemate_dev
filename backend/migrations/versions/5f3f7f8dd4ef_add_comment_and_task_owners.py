"""Add author/creator tracking to comments and tasks."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f3f7f8dd4ef"
down_revision: Union[str, Sequence[str], None] = "c0f269813939"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "comments",
        sa.Column("author_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_comments_author_id"), "comments", ["author_id"], unique=False
    )
    op.create_foreign_key(
        "fk_comments_author_id_users",
        "comments",
        "users",
        ["author_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "tasks",
        sa.Column("created_by_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_tasks_created_by_id"), "tasks", ["created_by_id"], unique=False
    )
    op.create_foreign_key(
        "fk_tasks_created_by_id_users",
        "tasks",
        "users",
        ["created_by_id"],
        ["id"],
        ondelete="SET NULL",
    )

    comments = sa.table(
        "comments",
        sa.column("id", sa.Integer()),
        sa.column("author", sa.String()),
        sa.column("author_id", sa.Integer()),
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
        comment_rows = bind.execute(sa.select(comments.c.id, comments.c.author)).all()
        for comment_id, author in comment_rows:
            if author:
                user_id = username_to_id.get(author)
                if user_id:
                    bind.execute(
                        sa.update(comments)
                        .where(comments.c.id == comment_id)
                        .values(author_id=user_id)
                    )


def downgrade() -> None:
    op.drop_constraint("fk_tasks_created_by_id_users", "tasks", type_="foreignkey")
    op.drop_index(op.f("ix_tasks_created_by_id"), table_name="tasks")
    op.drop_column("tasks", "created_by_id")

    op.drop_constraint("fk_comments_author_id_users", "comments", type_="foreignkey")
    op.drop_index(op.f("ix_comments_author_id"), table_name="comments")
    op.drop_column("comments", "author_id")
