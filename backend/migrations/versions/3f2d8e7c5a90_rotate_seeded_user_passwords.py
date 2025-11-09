"""rotate seeded user passwords"""

import os
from datetime import datetime
from typing import Dict

import sqlalchemy as sa
from alembic import op
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision = "3f2d8e7c5a90"
down_revision = "9b54f0f2e4b0"
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USER_SECRET_MAP: Dict[str, str] = {
    "globaladmin": "GLOBAL_ADMIN_PASSWORD",
    "phil": "HOME_ADMIN_PASSWORD",
    "courtney": "HOME_USER_PASSWORD",
}


def _get_required_secret(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Environment variable '{name}' must be set before applying migration {revision}."
        )
    return value


def upgrade() -> None:
    users_table = sa.table(
        "users",
        sa.column("username", sa.String(length=255)),
        sa.column("hashed_password", sa.String(length=255)),
        sa.column("updated_at", sa.DateTime()),
    )
    connection = op.get_bind()
    now = datetime.utcnow()

    for username, env_var in USER_SECRET_MAP.items():
        password = _get_required_secret(env_var)
        statement = (
            sa.update(users_table)
            .where(users_table.c.username == username)
            .values(
                hashed_password=pwd_context.hash(password),
                updated_at=now,
            )
        )
        result = connection.execute(statement)
        if result.rowcount == 0:
            raise RuntimeError(
                f"Expected seeded user '{username}' to exist before applying migration {revision}."
            )


def downgrade() -> None:
    raise RuntimeError(
        f"Downgrading migration {revision} is not supported because it would reintroduce "
        "compromised default passwords."
    )
