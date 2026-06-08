"""Tests para C-20 perfil propio.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

from typing import Any
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password
from app.models.auth import AuthUser
from app.models.tenant import Tenant


@pytest.fixture
async def perfil_schema(db_engine: None):
    from app.core.database import get_sessionmaker
    from app.models.usuarios_asignaciones import Usuario  # noqa: F401
    from app.services.auth import login_rate_limiter

    login_rate_limiter.reset_all()

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS mensajes_internos, hilos_mensajes, "
                "asignaciones, usuarios, cohortes, carreras, materias, "
                "roles_permisos, permisos, roles, "
                "password_recovery_tokens, two_factor_challenges, "
                "totp_factors, refresh_sessions, auth_users, tenants CASCADE"
            )
        )
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


@pytest.fixture
async def seed_perfil(db_session: AsyncSession) -> dict[str, Any]:
    tenant = Tenant(name="Tenant test", code="test")
    db_session.add(tenant)
    await db_session.flush()

    user = AuthUser(
        tenant_id=tenant.id,
        email="user@test.com",
        password_hash=hash_password("password"),
        roles=["ALUMNO"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    from app.core.encryption import encrypt_sensitive_value
    from app.models.usuarios_asignaciones import Usuario

    from app.core.config import Settings
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    encryption_key = settings.ENCRYPTION_KEY

    usuario = Usuario(
        tenant_id=tenant.id,
        nombre="Juan",
        apellidos="Pérez",
        email=encrypt_sensitive_value("juan@test.com", encryption_key=encryption_key),
        email_hash="abc123",
        dni=encrypt_sensitive_value("12345678", encryption_key=encryption_key),
        cuil=encrypt_sensitive_value("20-12345678-9", encryption_key=encryption_key),
        cbu=encrypt_sensitive_value("00000031000000000001", encryption_key=encryption_key),
        alias_cbu=encrypt_sensitive_value("JUAN.ALIAS", encryption_key=encryption_key),
        telefono="3511234567",
        banco="Banco Santander",
        regional="Córdoba",
        modalidad_cobro="liquidacion",
    )
    db_session.add(usuario)
    await db_session.flush()
    await db_session.commit()

    return {
        "tenant_id": tenant.id,
        "tenant_code": tenant.code,
        "user_id": user.id,
        "usuario_id": usuario.id,
    }


async def login(client: AsyncClient, tenant_code: str = "test", email: str = "user@test.com") -> dict[str, Any]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": "password"},
    )
    return resp.json()


async def auth_headers(client: AsyncClient, tenant_code: str = "test", email: str = "user@test.com") -> dict[str, str]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": "password"},
    )
    data = resp.json()
    assert "access_token" in data, f"Login failed for {email}@{tenant_code}: {data}"
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.mark.usefixtures("perfil_schema", "seed_perfil")
class TestGetPerfil:
    async def test_get_own_profile(self, async_client: AsyncClient):
        headers = await auth_headers(async_client)
        resp = await async_client.get("/api/v1/perfil", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["nombre"] == "Juan"
        assert data["apellidos"] == "Pérez"
        assert data["email"] == "juan@test.com"
        assert data["cuil"] == "20-12345678-9"
        assert data["cbu"] == "00000031000000000001"
        assert data["regional"] == "Córdoba"
        assert data["modalidad_cobro"] == "liquidacion"

    async def test_profile_includes_pii_decrypted(self, async_client: AsyncClient):
        headers = await auth_headers(async_client)
        resp = await async_client.get("/api/v1/perfil", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["dni"] == "12345678"
        assert data["cuil"] == "20-12345678-9"

    async def test_identity_from_jwt_not_param(self, async_client: AsyncClient):
        headers = await auth_headers(async_client)
        resp = await async_client.get("/api/v1/perfil", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] is not None


@pytest.mark.usefixtures("perfil_schema", "seed_perfil")
class TestUpdatePerfil:
    async def test_update_editable_fields(self, async_client: AsyncClient):
        headers = await auth_headers(async_client)
        resp = await async_client.put(
            "/api/v1/perfil",
            headers=headers,
            json={"nombre": "NewName", "banco": "Banco Nación", "telefono": "3519999999"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["nombre"] == "NewName"
        assert data["banco"] == "Banco Nación"
        assert data["telefono"] == "3519999999"
        assert data["apellidos"] == "Pérez"

    async def test_partial_update_only_changes_provided_fields(self, async_client: AsyncClient):
        headers = await auth_headers(async_client)
        resp = await async_client.put(
            "/api/v1/perfil",
            headers=headers,
            json={"telefono": "3511111111"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["telefono"] == "3511111111"
        assert data["nombre"] == "Juan"

    async def test_unauthorized_returns_401(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/perfil")
        assert resp.status_code == 401

    async def test_email_uniqueness_conflict(self, async_client: AsyncClient, db_session: AsyncSession):
        from app.core.encryption import encrypt_sensitive_value
        from app.models.usuarios_asignaciones import Usuario
        from app.core.config import Settings

        settings = Settings(_env_file=None)  # type: ignore[call-arg]
        seed = await _get_seed_tenant(db_session)
        otro = Usuario(
            tenant_id=seed["tenant_id"],
            nombre="Otro",
            apellidos="User",
            email=encrypt_sensitive_value("otro@test.com", encryption_key=settings.ENCRYPTION_KEY),
            email_hash="def456",
        )
        db_session.add(otro)
        await db_session.flush()
        await db_session.commit()

        headers = await auth_headers(async_client)
        resp = await async_client.put(
            "/api/v1/perfil",
            headers=headers,
            json={"email": "otro@test.com"},
        )
        assert resp.status_code == 409


async def _get_seed_tenant(db_session: AsyncSession) -> dict[str, Any]:
    result = await db_session.execute(
        text("SELECT id FROM tenants WHERE code = 'test'")
    )
    row = result.fetchone()
    return {"tenant_id": row[0]}
