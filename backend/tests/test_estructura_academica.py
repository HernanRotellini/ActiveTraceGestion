"""Tests para C-06 Estructura Académica: Carrera, Cohorte, Materia.

Strict TDD: RED (test that fails) → GREEN (minimum code) → TRIANGULATE → REFACTOR.
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


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
async def estructura_schema(db_engine: None):
    """Creates full schema with estructura academica tables."""
    from app.core.database import get_sessionmaker
    from app.models.estructura_academica import Carrera, Cohorte, Materia  # noqa: F401
    from app.services.auth import login_rate_limiter

    login_rate_limiter.reset_all()

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS cohortes, carreras, materias, "
                "roles_permisos, permisos, roles, "
                "password_recovery_tokens, two_factor_challenges, "
                "totp_factors, refresh_sessions, auth_users, tenants CASCADE"
            )
        )
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


@pytest.fixture
async def seed_tenant_admin(
    db_session: AsyncSession,
) -> dict[str, Any]:
    """Seeds tenant + admin user + estructura:gestionar permission. Returns context dict."""
    tenant = Tenant(name="Tenant test-tenant", code="test-tenant")
    db_session.add(tenant)
    await db_session.flush()

    user = AuthUser(
        tenant_id=tenant.id,
        email="user@test.com",
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
        codigo="estructura:gestionar",
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

    return {"tenant_id": tenant.id, "tenant_code": tenant.code, "user_id": user.id}


async def login(client: AsyncClient, tenant_code: str = "test-tenant") -> dict[str, Any]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": "user@test.com", "password": "password"},
    )
    return resp.json()


async def admin_headers(client: AsyncClient, tenant_code: str = "test-tenant", email: str = "user@test.com") -> dict[str, str]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": "password"},
    )
    data = resp.json()
    assert "access_token" in data, f"Login failed for {email}@{tenant_code}: {data}"
    return {"Authorization": f"Bearer {data['access_token']}"}


# ═══════════════════════════════════════════════════════════════
# 7.1 — Carrera CRUD
# ═══════════════════════════════════════════════════════════════


class TestCarreraCRUD:
    """RED → GREEN: Carrera CRUD operations."""

    async def test_create_carrera_returns_201_with_estado_activa(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura en Programacion"},
            headers=headers,
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["codigo"] == "TUPAD"
        assert data["nombre"] == "Tecnicatura en Programacion"
        assert data["estado"] == "activa"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_carrera_duplicate_codigo_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Original"},
            headers=headers,
        )
        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Duplicate"},
            headers=headers,
        )

        assert resp.status_code == 409

    async def test_same_codigo_different_tenant_succeeds(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        t2 = Tenant(name="Tenant t2", code="t2")
        db_session.add(t2)
        await db_session.flush()
        u2 = AuthUser(
            tenant_id=t2.id, email="u2@test.com",
            password_hash=hash_password("password"), roles=["ADMIN"], is_active=True,
        )
        db_session.add(u2)
        from app.models.rbac import Permiso, Rol, RolPermiso
        r2 = Rol(tenant_id=t2.id, codigo="ADMIN", nombre="Admin")
        db_session.add(r2)
        p2 = Permiso(tenant_id=t2.id, codigo="estructura:gestionar", nombre="Gestionar", modulo="estructura", accion="gestionar")
        db_session.add(p2)
        await db_session.flush()
        db_session.add(RolPermiso(tenant_id=t2.id, rol_id=r2.id, permiso_id=p2.id, habilitado=True, alcance="global"))
        await db_session.commit()

        h1 = await admin_headers(async_client)
        r1 = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "T1"}, headers=h1)
        assert r1.status_code == 201

        h2 = await admin_headers(async_client, "t2", "u2@test.com")
        r2 = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "T2"}, headers=h2)
        assert r2.status_code == 201

    async def test_list_carreras_returns_tenant_scoped(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "TUPAD"}, headers=headers)
        await async_client.post("/api/admin/carreras", json={"codigo": "TSSD", "nombre": "TSSD"}, headers=headers)

        resp = await async_client.get("/api/admin/carreras", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert {"TUPAD", "TSSD"} == {c["codigo"] for c in data}

    async def test_update_carrera_name(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Original"}, headers=headers)
        cid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/carreras/{cid}", json={"nombre": "Updated"}, headers=headers)

        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Updated"

    async def test_toggle_carrera_estado_inactiva(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Test"}, headers=headers)
        cid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/carreras/{cid}", json={"estado": "inactiva"}, headers=headers)

        assert resp.status_code == 200
        assert resp.json()["estado"] == "inactiva"

    async def test_soft_delete_carrera(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "DEL", "nombre": "Delete Me"}, headers=headers)
        cid = created.json()["id"]

        delete_resp = await async_client.delete(f"/api/admin/carreras/{cid}", headers=headers)
        assert delete_resp.status_code == 204

        get_resp = await async_client.get(f"/api/admin/carreras/{cid}", headers=headers)
        assert get_resp.status_code == 404

    async def test_tenant_a_cannot_see_tenant_b_carreras(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        t2 = Tenant(name="Tenant t2", code="t2")
        db_session.add(t2)
        await db_session.flush()
        u2 = AuthUser(tenant_id=t2.id, email="u2@test.com", password_hash=hash_password("password"), roles=["ADMIN"], is_active=True)
        db_session.add(u2)
        from app.models.rbac import Permiso, Rol, RolPermiso
        r2 = Rol(tenant_id=t2.id, codigo="ADMIN", nombre="Admin")
        db_session.add(r2)
        p2 = Permiso(tenant_id=t2.id, codigo="estructura:gestionar", nombre="Gestionar", modulo="estructura", accion="gestionar")
        db_session.add(p2)
        await db_session.flush()
        db_session.add(RolPermiso(tenant_id=t2.id, rol_id=r2.id, permiso_id=p2.id, habilitado=True, alcance="global"))
        await db_session.commit()

        h1 = await admin_headers(async_client)
        h2 = await admin_headers(async_client, "t2", "u2@test.com")

        await async_client.post("/api/admin/carreras", json={"codigo": "T1", "nombre": "T1"}, headers=h1)
        await async_client.post("/api/admin/carreras", json={"codigo": "T2", "nombre": "T2"}, headers=h2)

        resp = await async_client.get("/api/admin/carreras", headers=h1)
        codigos = [c["codigo"] for c in resp.json()]
        assert "T1" in codigos
        assert "T2" not in codigos


# ═══════════════════════════════════════════════════════════════
# 7.2 — Cohorte CRUD
# ═══════════════════════════════════════════════════════════════


class TestCohorteCRUD:
    """RED → GREEN: Cohorte CRUD operations."""

    @pytest.fixture
    async def carrera_id(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> str:
        headers = await admin_headers(async_client)
        resp = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "TUPAD"}, headers=headers)
        return resp.json()["id"]

    async def test_create_cohorte_returns_201(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "MAR-2026"
        assert data["anio"] == 2026
        assert data["estado"] == "activa"
        assert data["carrera_id"] == carrera_id
        assert "id" in data

    async def test_create_cohorte_on_inactive_carrera_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.patch(f"/api/admin/carreras/{carrera_id}", json={"estado": "inactiva"}, headers=headers)

        resp = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )

        assert resp.status_code == 409

    async def test_create_cohorte_nonexistent_carrera_returns_404(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        fake_id = "00000000-0000-0000-0000-000000000000"

        resp = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": fake_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )

        assert resp.status_code == 404

    async def test_create_cohorte_duplicate_name_in_same_carrera_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        resp = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2027, "vig_desde": "2027-03-01"},
            headers=headers,
        )

        assert resp.status_code == 409

    async def test_same_cohorte_name_different_carrera_succeeds(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        c2_resp = await async_client.post("/api/admin/carreras", json={"codigo": "TSSD", "nombre": "TSSD"}, headers=headers)
        c2_id = c2_resp.json()["id"]

        r1 = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        assert r1.status_code == 201

        r2 = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": c2_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        assert r2.status_code == 201

    async def test_list_cohortes_by_carrera(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        c2_resp = await async_client.post("/api/admin/carreras", json={"codigo": "TSSD", "nombre": "TSSD"}, headers=headers)
        c2_id = c2_resp.json()["id"]

        for cid in [carrera_id, c2_id]:
            await async_client.post(
                "/api/admin/cohortes",
                json={"carrera_id": cid, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
                headers=headers,
            )

        resp = await async_client.get(f"/api/admin/cohortes?carrera_id={carrera_id}", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["carrera_id"] == carrera_id


# ═══════════════════════════════════════════════════════════════
# 7.3 — Materia CRUD
# ═══════════════════════════════════════════════════════════════


class TestMateriaCRUD:
    """RED → GREEN: Materia CRUD operations."""

    async def test_create_materia_returns_201(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "Programacion I"},
            headers=headers,
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["codigo"] == "PROG_I"
        assert data["nombre"] == "Programacion I"
        assert data["estado"] == "activa"
        assert "id" in data

    async def test_create_materia_duplicate_codigo_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "Original"}, headers=headers)
        resp = await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "Duplicate"}, headers=headers)

        assert resp.status_code == 409

    async def test_same_materia_codigo_different_tenant_succeeds(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        t2 = Tenant(name="Tenant t2", code="t2")
        db_session.add(t2)
        await db_session.flush()
        u2 = AuthUser(tenant_id=t2.id, email="u2@test.com", password_hash=hash_password("password"), roles=["ADMIN"], is_active=True)
        db_session.add(u2)
        from app.models.rbac import Permiso, Rol, RolPermiso
        r2 = Rol(tenant_id=t2.id, codigo="ADMIN", nombre="Admin")
        db_session.add(r2)
        p2 = Permiso(tenant_id=t2.id, codigo="estructura:gestionar", nombre="Gestionar", modulo="estructura", accion="gestionar")
        db_session.add(p2)
        await db_session.flush()
        db_session.add(RolPermiso(tenant_id=t2.id, rol_id=r2.id, permiso_id=p2.id, habilitado=True, alcance="global"))
        await db_session.commit()

        h1 = await admin_headers(async_client)
        h2 = await admin_headers(async_client, "t2", "u2@test.com")

        r1 = await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "T1"}, headers=h1)
        assert r1.status_code == 201
        r2 = await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "T2"}, headers=h2)
        assert r2.status_code == 201

    async def test_list_materias(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "Prog I"}, headers=headers)
        await async_client.post("/api/admin/materias", json={"codigo": "PROG_II", "nombre": "Prog II"}, headers=headers)

        resp = await async_client.get("/api/admin/materias", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_soft_delete_materia(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/materias", json={"codigo": "DEL", "nombre": "Delete Me"}, headers=headers)
        mid = created.json()["id"]

        delete_resp = await async_client.delete(f"/api/admin/materias/{mid}", headers=headers)
        assert delete_resp.status_code == 204

        get_resp = await async_client.get(f"/api/admin/materias/{mid}", headers=headers)
        assert get_resp.status_code == 404

    async def test_update_materia(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "Original"}, headers=headers)
        mid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/materias/{mid}", json={"nombre": "Updated"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Updated"

    async def test_tenant_a_cannot_update_tenant_b_materia(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        t2 = Tenant(name="Tenant t2", code="t2")
        db_session.add(t2)
        await db_session.flush()
        u2 = AuthUser(tenant_id=t2.id, email="u2@test.com", password_hash=hash_password("password"), roles=["ADMIN"], is_active=True)
        db_session.add(u2)
        from app.models.rbac import Permiso, Rol, RolPermiso
        r2 = Rol(tenant_id=t2.id, codigo="ADMIN", nombre="Admin")
        db_session.add(r2)
        p2 = Permiso(tenant_id=t2.id, codigo="estructura:gestionar", nombre="Gestionar", modulo="estructura", accion="gestionar")
        db_session.add(p2)
        await db_session.flush()
        db_session.add(RolPermiso(tenant_id=t2.id, rol_id=r2.id, permiso_id=p2.id, habilitado=True, alcance="global"))
        await db_session.commit()

        h2 = await admin_headers(async_client, "t2", "u2@test.com")
        created = await async_client.post("/api/admin/materias", json={"codigo": "T2", "nombre": "T2"}, headers=h2)
        mid = created.json()["id"]

        h1 = await admin_headers(async_client)
        resp = await async_client.patch(f"/api/admin/materias/{mid}", json={"nombre": "Hacked"}, headers=h1)
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
# 7.4 — Auth guard
# ═══════════════════════════════════════════════════════════════


class TestAuthGuard:
    """All estructura endpoints require estructura:gestionar → 403 without it."""

    async def test_endpoints_return_403_without_estructura_gestionar(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
    ) -> None:
        tenant = Tenant(name="Tenant test", code="test")
        db_session.add(tenant)
        await db_session.flush()
        user = AuthUser(
            tenant_id=tenant.id, email="user@test.com",
            password_hash=hash_password("password"), roles=["TUTOR"], is_active=True,
        )
        db_session.add(user)
        from app.models.rbac import Rol
        db_session.add(Rol(tenant_id=tenant.id, codigo="TUTOR", nombre="Tutor"))
        await db_session.commit()

        resp = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "test", "email": "user@test.com", "password": "password"},
        )
        data = resp.json()
        assert "access_token" in data, f"Login failed: {data}"
        headers = {"Authorization": f"Bearer {data['access_token']}"}

        endpoints = [
            ("GET", "/api/admin/carreras"),
            ("POST", "/api/admin/carreras"),
            ("GET", "/api/admin/cohortes"),
            ("POST", "/api/admin/cohortes"),
            ("GET", "/api/admin/materias"),
            ("POST", "/api/admin/materias"),
        ]
        for method, url in endpoints:
            if method == "GET":
                resp = await async_client.get(url, headers=headers)
            else:
                resp = await async_client.post(url, json={}, headers=headers)
            assert resp.status_code == 403, f"{method} {url} expected 403, got {resp.status_code}"
