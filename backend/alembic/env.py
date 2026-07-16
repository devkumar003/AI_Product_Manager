import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.settings import settings
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override database connection URL from settings
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

target_metadata = Base.metadata


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
        # Auto-stamp logic for pre-existing production databases
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(connection)
            tables = inspector.get_table_names()
            
            if "integration_plugins" in tables and "ai_workflow_executions" not in tables:
                has_version = False
                if "alembic_version" in tables:
                    try:
                        res = connection.execute(text("SELECT version_num FROM alembic_version")).fetchone()
                        if res:
                            has_version = True
                    except Exception:
                        pass
                
                if not has_version:
                    if "alembic_version" not in tables:
                        connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, PRIMARY KEY (version_num))"))
                    connection.execute(text("DELETE FROM alembic_version"))
                    connection.execute(text("INSERT INTO alembic_version (version_num) VALUES ('9a61dadb18c7')"))
                    try:
                        connection.commit()
                    except Exception:
                        pass
                    print("Auto-healed database: Stamped Alembic version to 9a61dadb18c7")
        except Exception as e:
            print(f"Alembic auto-stamping warning: {e}")

        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
