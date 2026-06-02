"""Tests de migración Alembic para foundation tenant."""

import asyncio
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine


def alembic_config() -> Config:
    """Configura Alembic desde el directorio backend."""
    backend_dir = Path(__file__).resolve().parents[1]
    return Config(str(backend_dir / "alembic.ini"))


async def drop_tenant_schema() -> None:
    """Limpia tablas creadas por tests/migraciones tenant."""
    engine = create_async_engine(os.environ["DATABASE_URL"])
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS password_recovery_tokens, two_factor_challenges, "
                "totp_factors, refresh_sessions, auth_users, test_repository_records, "
                "test_scoped_records, tenants CASCADE"
            )
        )
        await connection.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
    await engine.dispose()


async def table_exists(table_name: str) -> bool:
    """Inspecciona existencia de tabla contra PostgreSQL real."""
    engine = create_async_engine(os.environ["DATABASE_URL"])
    async with engine.connect() as connection:
        exists = await connection.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table(table_name)
        )
    await engine.dispose()
    return exists


async def table_columns(table_name: str) -> set[str]:
    """Lista columnas de una tabla contra PostgreSQL real."""
    engine = create_async_engine(os.environ["DATABASE_URL"])
    async with engine.connect() as connection:
        columns = await connection.run_sync(
            lambda sync_conn: {column["name"] for column in inspect(sync_conn).get_columns(table_name)}
        )
    await engine.dispose()
    return columns


def test_tenant_migration_creates_and_rolls_back_tenants_table() -> None:
    asyncio.run(drop_tenant_schema())

    command.upgrade(alembic_config(), "head")

    assert asyncio.run(table_exists("tenants")) is True

    command.downgrade(alembic_config(), "base")
    assert asyncio.run(table_exists("tenants")) is False


def test_auth_migration_creates_and_rolls_back_auth_users_table() -> None:
    asyncio.run(drop_tenant_schema())

    command.upgrade(alembic_config(), "head")

    assert asyncio.run(table_exists("auth_users")) is True
    assert asyncio.run(table_exists("refresh_sessions")) is True
    assert asyncio.run(table_exists("totp_factors")) is True
    assert asyncio.run(table_exists("two_factor_challenges")) is True
    assert asyncio.run(table_exists("password_recovery_tokens")) is True
    assert {
        "id",
        "tenant_id",
        "email",
        "password_hash",
        "roles",
        "is_active",
        "created_at",
        "updated_at",
        "deleted_at",
    }.issubset(asyncio.run(table_columns("auth_users")))

    command.downgrade(alembic_config(), "20260602_0001")
    assert asyncio.run(table_exists("auth_users")) is False
    assert asyncio.run(table_exists("refresh_sessions")) is False
