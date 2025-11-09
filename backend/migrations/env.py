import os
from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.database import Base, DATABASE_URL, CONNECT_ARGS
from app.models import Comment, Task, Ticket, User  # ensure models are imported


REQUIRED_PASSWORD_ENV_VARS = (
    "GLOBAL_ADMIN_PASSWORD",
    "HOME_ADMIN_PASSWORD",
    "HOME_USER_PASSWORD",
)

missing_env_vars = [name for name in REQUIRED_PASSWORD_ENV_VARS if not os.getenv(name)]
if missing_env_vars:
    joined = ", ".join(sorted(missing_env_vars))
    raise RuntimeError(
        "Missing required environment variable(s) for seeded user credentials: "
        f"{joined}. Set them before running Alembic migrations."
    )

config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args=CONNECT_ARGS,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
