"""Contract test: POST /api/admin/cohortes payload matches backend schema."""
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password
from app.models.auth import AuthUser
from app.models.permisos import ESTRUCTURA_GESTIONAR
from app.models.tenant import Tenant


@pytest.fixture
async def schema(db_engine: None) -> None:
    from app.core.database import get_sessionmaker
    from app.models.auth import AuthUser  # noqa: F401
    from app.models.estructura_academica import Carrera, Cohorte  # noqa: F401
    from app.models.rbac import Permiso, Rol, RolPermiso  # noqa: F401
    from app.models.tenant import Tenant  # noqa: F401
    from app.services.auth import login_rate_limiter

    login_rate_limiter.reset_all()
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        conn = await session.connection()
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.create_all)
        await session.commit()


@pytest.fixture
async def context(db_session: AsyncSession, schema: None) -> dict[str, Any]:
    tenant = Tenant(name="Tenant test", code=f"cohorte-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()

    user = AuthUser(
        tenant_id=tenant.id,
        email="admin@test.com",
        password_hash=hash_password("password"),
        roles=["ADMIN"],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    from app.models.rbac import Permiso, Rol, RolPermiso

    rol = Rol(tenant_id=tenant.id, codigo="ADMIN", nombre="Admin")
    db_session.add(rol)
    permiso = Permiso(
        tenant_id=tenant.id,
        codigo=ESTRUCTURA_GESTIONAR,
        nombre="Gestionar estructura academica",
        modulo="estructura",
        accion="gestionar",
    )
    db_session.add(permiso)
    await db_session.flush()

    rp = RolPermiso(
        tenant_id=tenant.id,
        rol_id=rol.id,
        permiso_id=permiso.id,
        habilitado=True,
        alcance="global",
    )
    db_session.add(rp)
    await db_session.flush()
    await db_session.commit()

    return {"tenant_id": tenant.id, "tenant_code": tenant.code}


async def headers(client: AsyncClient, ctx: dict[str, Any]) -> dict[str, str]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": ctx["tenant_code"], "email": "admin@test.com", "password": "password"},
    )
    data = resp.json()
    assert "access_token" in data
    return {"Authorization": f"Bearer {data['access_token']}"}


class TestCohorteContract:
    @pytest.fixture
    async def carrera_id(
        self, db_session: AsyncSession, async_client: AsyncClient, context: dict[str, Any],
    ) -> str:
        hdrs = await headers(async_client, context)
        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "COH-TEST", "nombre": "Cohorte Test Carrera"},
            headers=hdrs,
        )
        assert resp.status_code == 201
        return resp.json()["id"]

    async def test_correct_payload_returns_201(
        self, db_session: AsyncSession, async_client: AsyncClient, context: dict[str, Any],
        carrera_id: str,
    ) -> None:
        hdrs = await headers(async_client, context)
        resp = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "Test Cohorte", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=hdrs,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "id" in data
        assert data["carrera_id"] == carrera_id
        assert data["nombre"] == "Test Cohorte"
        assert data["anio"] == 2026

    async def test_unknown_field_returns_422(
        self, db_session: AsyncSession, async_client: AsyncClient, context: dict[str, Any],
        carrera_id: str,
    ) -> None:
        hdrs = await headers(async_client, context)
        resp = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "Test", "anio": 2026, "vig_desde": "2026-03-01", "activo": True},
            headers=hdrs,
        )
        assert resp.status_code == 422
