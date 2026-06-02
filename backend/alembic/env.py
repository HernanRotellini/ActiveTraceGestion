"""Configuración de Alembic para engine async (asyncpg + SQLAlchemy 2.0).

Las migraciones se ejecutan en modo asíncrono. Cada migración de dominio
se crea con `alembic revision --autogenerate -m "descripcion"`.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import Settings
from app.core.database import Base
import app.models  # noqa: F401

# Alembic Config object
config = context.config

# Configurar logging si alembic.ini tiene logger config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata objetivo para autogenerate
target_metadata = Base.metadata

# ── Cargar DATABASE_URL desde Settings ────────────────────────
settings = Settings()  # type: ignore[call-arg]
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Ejecuta migraciones offline (genera SQL sin conexión).

    Útil para revisar el SQL generado antes de aplicarlo.
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


def do_run_migrations(connection: Connection) -> None:
    """Ejecuta migraciones sobre una conexión dada."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Ejecuta migraciones async usando async engine.

    Crea un engine desde la config, ejecuta migraciones y lo cierra.
    """
    configuration = config.get_section(config.config_ini_section, {})
    assert configuration is not None
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Ejecuta migraciones online (async)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
