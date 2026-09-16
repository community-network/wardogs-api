from logging.config import fileConfig

from sqlalchemy import URL, engine_from_config, pool

from alembic import context
from app.database import connection
from app.database.dto import (  # noqa: F401
    discord_user,
    stats_snapshot,
    unlock,
    wardogs_account,
)

# add db items to autogenerate the migrations
from config import load_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

env_config = load_config()

uri = URL.create(
    drivername="postgresql",
    username=env_config.db.postgres_user,
    password=env_config.db.postgres_password,
    host=env_config.db.db_host,
    port=env_config.db.db_port,
    database=env_config.db.postgres_db,
)
url = uri.render_as_string(hide_password=False).replace("%", "%%")
config.set_main_option("sqlalchemy.url", url)

# add your model's MetaData object here
# for 'autogenerate' support

target_metadata = connection.Base.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
