"""add users table"""

from datetime import datetime

import sqlalchemy as sa
from alembic import op
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision = "9b54f0f2e4b0"
down_revision = "7cbf4444bc7c"
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user_role_enum = sa.Enum("global_admin", "home_admin", "home_user", name="userrole")


def upgrade() -> None:
    bind = op.get_bind()
    user_role_enum.create(bind, checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )

    users_table = sa.table(
        "users",
        sa.column("username", sa.String(length=255)),
        sa.column("role", sa.String(length=50)),
        sa.column("hashed_password", sa.String(length=255)),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )
    now = datetime.utcnow()
    op.bulk_insert(
        users_table,
        [
            {
                "username": "globaladmin",
                "role": "global_admin",
                "hashed_password": pwd_context.hash("ChangeMe123!"),
                "created_at": now,
                "updated_at": now,
            },
            {
                "username": "phil",
                "role": "home_admin",
                "hashed_password": pwd_context.hash("PhilRocks123!"),
                "created_at": now,
                "updated_at": now,
            },
            {
                "username": "courtney",
                "role": "home_user",
                "hashed_password": pwd_context.hash("CourtneySecure123!"),
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("users")
    user_role_enum.drop(op.get_bind(), checkfirst=True)
