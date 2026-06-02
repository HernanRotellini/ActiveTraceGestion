"""Tests de modelos y repositories mínimos de autenticación."""

from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.models.auth import AuthUser
from app.models.tenant import Tenant
from app.repositories.auth import AuthUserRepository


@pytest.fixture
async def auth_schema(db_engine: None):
    async with _metadata_context():
        yield


class _metadata_context:
    async def __aenter__(self) -> None:
        from app.core.database import get_sessionmaker

        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            connection = await session.connection()
            await connection.execute(
                text("DROP TABLE IF EXISTS auth_users, tenants CASCADE")
            )
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)
            await session.commit()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        from app.core.database import get_sessionmaker

        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            connection = await session.connection()
            await connection.execute(
                text("DROP TABLE IF EXISTS auth_users, tenants CASCADE")
            )
            await session.commit()


async def create_tenant(db_session: AsyncSession, code: str) -> Tenant:
    tenant = Tenant(name=f"Tenant {code}", code=code)
    db_session.add(tenant)
    await db_session.flush()
    return tenant


class TestAuthUserModel:
    async def test_auth_user_is_tenant_scoped_and_stores_argon2id_hash(
        self, auth_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session, "auth-a")
        user = AuthUser(
            tenant_id=tenant.id,
            email="user@example.com",
            password_hash="$argon2id$v=19$m=65536,t=3,p=4$abc$def",
            roles=["ALUMNO"],
        )

        db_session.add(user)
        await db_session.flush()

        assert user.id is not None
        assert user.tenant_id == tenant.id
        assert user.password_hash.startswith("$argon2id$")
        assert user.is_active is True

    async def test_auth_user_can_be_inactive(self, auth_schema: None, db_session: AsyncSession) -> None:
        tenant = await create_tenant(db_session, "auth-inactive")
        user = AuthUser(
            tenant_id=tenant.id,
            email="inactive@example.com",
            password_hash="$argon2id$v=19$m=65536,t=3,p=4$abc$def",
            roles=["TUTOR"],
            is_active=False,
        )

        db_session.add(user)
        await db_session.flush()

        assert user.is_active is False


class TestAuthUserRepository:
    async def test_get_by_email_is_tenant_scoped(
        self, auth_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_a = await create_tenant(db_session, "auth-tenant-a")
        tenant_b = await create_tenant(db_session, "auth-tenant-b")
        db_session.add_all(
            [
                AuthUser(
                    tenant_id=tenant_a.id,
                    email="shared@example.com",
                    password_hash="$argon2id$v=19$m=65536,t=3,p=4$a$b",
                    roles=["ALUMNO"],
                ),
                AuthUser(
                    tenant_id=tenant_b.id,
                    email="shared@example.com",
                    password_hash="$argon2id$v=19$m=65536,t=3,p=4$c$d",
                    roles=["ADMIN"],
                ),
            ]
        )
        await db_session.flush()

        repository = AuthUserRepository(db_session, tenant_id=tenant_a.id)
        user = await repository.get_by_email("SHARED@example.com")

        assert user is not None
        assert user.tenant_id == tenant_a.id
        assert user.roles == ["ALUMNO"]

    async def test_get_by_email_ignores_soft_deleted_users(
        self, auth_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session, "auth-soft")
        user = AuthUser(
            tenant_id=tenant.id,
            email="deleted@example.com",
            password_hash="$argon2id$v=19$m=65536,t=3,p=4$a$b",
            roles=["ALUMNO"],
        )
        db_session.add(user)
        await db_session.flush()

        repository = AuthUserRepository(db_session, tenant_id=tenant.id)
        await repository.soft_delete(user.id)
        await db_session.flush()

        assert await repository.get_by_email("deleted@example.com") is None
