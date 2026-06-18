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
    from app.models.audit_log import AuditLog  # noqa: F401
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401
    from app.services.auth import login_rate_limiter

    login_rate_limiter.reset_all()

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS "
                "slots_encuentro, guardias, comision_docentes, comisiones, "
                "asignaciones, cohortes, carreras, materias, "
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

    async def test_create_carrera_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import CARRERA_CREAR
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura en Programacion"},
            headers=headers,
        )

        assert resp.status_code == 201
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == CARRERA_CREAR))
        audit = result.scalar_one()
        assert audit.detalle["carrera_id"] == resp.json()["id"]
        assert audit.detalle["codigo"] == "TUPAD"
        assert audit.detalle["nombre"] == "Tecnicatura en Programacion"
        assert audit.filas_afectadas == 1

    async def test_create_carrera_can_start_inactiva(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura en Programacion", "estado": "inactiva"},
            headers=headers,
        )

        assert resp.status_code == 201
        assert resp.json()["estado"] == "inactiva"

    async def test_create_carrera_invalid_estado_returns_422(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura en Programacion", "estado": "pausada"},
            headers=headers,
        )

        assert resp.status_code == 422

    async def test_create_carrera_blank_required_fields_return_422(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": " ", "nombre": ""},
            headers=headers,
        )

        assert resp.status_code == 422

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

    async def test_create_carrera_duplicate_nombre_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura"},
            headers=headers,
        )
        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TSSD", "nombre": "Tecnicatura"},
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

    async def test_same_nombre_different_tenant_succeeds(
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
        r1 = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Tecnicatura"}, headers=h1)
        assert r1.status_code == 201

        h2 = await admin_headers(async_client, "t2", "u2@test.com")
        r2 = await async_client.post("/api/admin/carreras", json={"codigo": "TSSD", "nombre": "Tecnicatura"}, headers=h2)
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
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert {"TUPAD", "TSSD"} == {c["codigo"] for c in data["items"]}

    async def test_list_carreras_filters_by_codigo_nombre_and_estado(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura en Programacion"},
            headers=headers,
        )
        sistemas = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TSSD", "nombre": "Sistemas"},
            headers=headers,
        )
        await async_client.patch(
            f"/api/admin/carreras/{sistemas.json()['id']}",
            json={"estado": "inactiva"},
            headers=headers,
        )

        by_codigo = await async_client.get("/api/admin/carreras", params={"codigo": "TUP"}, headers=headers)
        by_nombre = await async_client.get("/api/admin/carreras", params={"nombre": "sist"}, headers=headers)
        by_estado = await async_client.get("/api/admin/carreras", params={"estado": "inactiva"}, headers=headers)

        assert [c["codigo"] for c in by_codigo.json()["items"]] == ["TUPAD"]
        assert [c["codigo"] for c in by_nombre.json()["items"]] == ["TSSD"]
        assert [c["codigo"] for c in by_estado.json()["items"]] == ["TSSD"]

    async def test_list_carreras_invalid_estado_filter_returns_422(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.get("/api/admin/carreras", params={"estado": "pausada"}, headers=headers)

        assert resp.status_code == 422

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

    async def test_update_carrera_general_fields_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import CARRERA_EDITAR
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Original"}, headers=headers)
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/carreras/{cid}",
            json={"codigo": "TUP", "nombre": "Updated", "descripcion": "Nueva descripcion"},
            headers=headers,
        )

        assert resp.status_code == 200
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == CARRERA_EDITAR))
        audit = result.scalar_one()
        assert audit.detalle["carrera_id"] == cid
        assert audit.detalle["cambios"]["codigo"] == {"anterior": "TUPAD", "nuevo": "TUP"}
        assert audit.detalle["cambios"]["nombre"] == {"anterior": "Original", "nuevo": "Updated"}
        assert audit.detalle["cambios"]["descripcion"] == {"anterior": "", "nuevo": "Nueva descripcion"}
        assert audit.filas_afectadas == 1

    async def test_update_carrera_duplicate_nombre_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        first = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Tecnicatura"}, headers=headers)
        second = await async_client.post("/api/admin/carreras", json={"codigo": "TSSD", "nombre": "Sistemas"}, headers=headers)
        second_id = second.json()["id"]

        resp = await async_client.patch(f"/api/admin/carreras/{second_id}", json={"nombre": first.json()["nombre"]}, headers=headers)

        assert resp.status_code == 409

    async def test_update_carrera_duplicate_codigo_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        first = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Tecnicatura"}, headers=headers)
        second = await async_client.post("/api/admin/carreras", json={"codigo": "TSSD", "nombre": "Sistemas"}, headers=headers)
        second_id = second.json()["id"]

        resp = await async_client.patch(f"/api/admin/carreras/{second_id}", json={"codigo": first.json()["codigo"]}, headers=headers)

        assert resp.status_code == 409

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

    async def test_toggle_carrera_estado_activa(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Test", "estado": "inactiva"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/carreras/{cid}", json={"estado": "activa"}, headers=headers)

        assert resp.status_code == 200
        assert resp.json()["estado"] == "activa"

    async def test_toggle_carrera_estado_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import CARRERA_CAMBIAR_ESTADO
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Test"}, headers=headers)
        cid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/carreras/{cid}", json={"estado": "inactiva"}, headers=headers)

        assert resp.status_code == 200
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == CARRERA_CAMBIAR_ESTADO))
        audit = result.scalar_one()
        assert audit.detalle["carrera_id"] == cid
        assert audit.detalle["codigo"] == "TUPAD"
        assert audit.detalle["estado_anterior"] == "activa"
        assert audit.detalle["estado_nuevo"] == "inactiva"
        assert audit.filas_afectadas == 1

    async def test_update_carrera_without_estado_change_does_not_create_estado_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import CARRERA_CAMBIAR_ESTADO
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Test"}, headers=headers)
        cid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/carreras/{cid}", json={"nombre": "Test actualizado"}, headers=headers)

        assert resp.status_code == 200
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == CARRERA_CAMBIAR_ESTADO))
        assert result.scalars().all() == []

    async def test_update_carrera_invalid_estado_returns_422(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Test"}, headers=headers)
        cid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/carreras/{cid}", json={"estado": "pausada"}, headers=headers)

        assert resp.status_code == 422

    async def test_update_carrera_blank_required_fields_return_422(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "TUPAD", "nombre": "Test"}, headers=headers)
        cid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/carreras/{cid}", json={"codigo": "", "nombre": " "}, headers=headers)

        assert resp.status_code == 422

    async def test_soft_delete_carrera(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "DEL", "nombre": "Delete Me"}, headers=headers)
        cid = created.json()["id"]
        await async_client.patch(f"/api/admin/carreras/{cid}", json={"estado": "inactiva"}, headers=headers)

        delete_resp = await async_client.delete(f"/api/admin/carreras/{cid}", headers=headers)
        assert delete_resp.status_code == 204

        get_resp = await async_client.get(f"/api/admin/carreras/{cid}", headers=headers)
        assert get_resp.status_code == 404

    async def test_soft_delete_carrera_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import CARRERA_ELIMINAR
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "DEL", "nombre": "Delete Me", "estado": "inactiva"}, headers=headers)
        cid = created.json()["id"]

        delete_resp = await async_client.delete(f"/api/admin/carreras/{cid}", headers=headers)

        assert delete_resp.status_code == 204
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == CARRERA_ELIMINAR))
        audit = result.scalar_one()
        assert audit.detalle["carrera_id"] == cid
        assert audit.detalle["codigo"] == "DEL"
        assert audit.detalle["nombre"] == "Delete Me"
        assert audit.filas_afectadas == 1

    async def test_delete_active_carrera_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "DEL", "nombre": "Delete Me"}, headers=headers)
        cid = created.json()["id"]

        delete_resp = await async_client.delete(f"/api/admin/carreras/{cid}", headers=headers)

        assert delete_resp.status_code == 409
        assert "active carrera" in delete_resp.json()["detail"]

    async def test_delete_carrera_with_cohortes_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "DEL", "nombre": "Delete Me"}, headers=headers)
        cid = created.json()["id"]
        await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": cid, "nombre": "2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        await async_client.patch(f"/api/admin/carreras/{cid}", json={"estado": "inactiva"}, headers=headers)

        delete_resp = await async_client.delete(f"/api/admin/carreras/{cid}", headers=headers)

        assert delete_resp.status_code == 409
        assert "associated cohortes" in delete_resp.json()["detail"]

    async def test_delete_carrera_with_asignaciones_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from datetime import date

        from app.models.usuarios_asignaciones import Asignacion, Usuario

        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/carreras", json={"codigo": "DEL", "nombre": "Delete Me"}, headers=headers)
        cid = created.json()["id"]
        usuario = Usuario(
            tenant_id=seed_tenant_admin["tenant_id"],
            nombre="Docente",
            apellidos="Test",
            email="docente@test.com",
        )
        db_session.add(usuario)
        await db_session.flush()
        db_session.add(
            Asignacion(
                tenant_id=seed_tenant_admin["tenant_id"],
                usuario_id=usuario.id,
                rol="PROFESOR",
                carrera_id=UUID(cid),
                desde=date(2026, 3, 1),
            )
        )
        await db_session.commit()
        await async_client.patch(f"/api/admin/carreras/{cid}", json={"estado": "inactiva"}, headers=headers)

        delete_resp = await async_client.delete(f"/api/admin/carreras/{cid}", headers=headers)

        assert delete_resp.status_code == 409
        assert "associated asignaciones" in delete_resp.json()["detail"]

    async def test_carrera_response_has_activo_and_creada_en(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura"},
            headers=headers,
        )

        data = resp.json()
        assert data["activo"] is True
        assert data["creada_en"] == data["created_at"]

        # toggle to inactive
        cid = data["id"]
        resp2 = await async_client.patch(f"/api/admin/carreras/{cid}", json={"estado": "inactiva"}, headers=headers)
        assert resp2.json()["activo"] is False

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
        codigos = [c["codigo"] for c in resp.json()["items"]]
        assert "T1" in codigos
        assert "T2" not in codigos

    async def test_tenant_a_cannot_delete_tenant_b_carrera(
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

        created = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "T2", "nombre": "T2", "estado": "inactiva"},
            headers=h2,
        )
        carrera_t2_id = created.json()["id"]

        delete_resp = await async_client.delete(f"/api/admin/carreras/{carrera_t2_id}", headers=h1)
        get_t2_resp = await async_client.get(f"/api/admin/carreras/{carrera_t2_id}", headers=h2)

        assert delete_resp.status_code == 404
        assert get_t2_resp.status_code == 200

    # ── Descripcion tests ─────────────────────────────────────

    async def test_create_carrera_with_descripcion_persists(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura", "descripcion": "Nueva tecnicatura"},
            headers=headers,
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["descripcion"] == "Nueva tecnicatura"

    async def test_create_carrera_without_descripcion_returns_empty(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura"},
            headers=headers,
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["descripcion"] == ""

    async def test_update_carrera_descripcion(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Original"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/carreras/{cid}",
            json={"descripcion": "Updated desc"},
            headers=headers,
        )

        assert resp.status_code == 200
        assert resp.json()["descripcion"] == "Updated desc"


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

    async def test_create_cohorte_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import COHORTE_CREAR
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/cohortes",
            json={
                "carrera_id": carrera_id,
                "nombre": "MAR-2026",
                "anio": 2026,
                "vig_desde": "2026-03-01",
                "vig_hasta": "2026-12-15",
            },
            headers=headers,
        )

        assert resp.status_code == 201
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == COHORTE_CREAR))
        audit = result.scalar_one()
        assert audit.detalle["cohorte_id"] == resp.json()["id"]
        assert audit.detalle["carrera_id"] == carrera_id
        assert audit.detalle["nombre"] == "MAR-2026"
        assert audit.detalle["anio"] == 2026
        assert audit.detalle["vig_desde"] == "2026-03-01"
        assert audit.detalle["vig_hasta"] == "2026-12-15"
        assert audit.filas_afectadas == 1

    async def test_create_cohorte_can_start_inactiva(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/cohortes",
            json={
                "carrera_id": carrera_id,
                "nombre": "AGO-2026",
                "anio": 2026,
                "vig_desde": "2026-08-01",
                "estado": "inactiva",
            },
            headers=headers,
        )

        assert resp.status_code == 201
        assert resp.json()["estado"] == "inactiva"

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

    async def test_create_cohorte_blank_name_returns_422(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "   ", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )

        assert resp.status_code == 422

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
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["carrera_id"] == carrera_id


    async def test_patch_cohorte_updates_fields(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/cohortes/{cid}",
            json={"nombre": "2027", "anio": 2027},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["nombre"] == "2027"
        assert data["anio"] == 2027

    async def test_patch_cohorte_updates_estado_and_vigencia(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/cohortes/{cid}",
            json={"vig_desde": "2026-04-01", "vig_hasta": "2026-12-15", "estado": "inactiva"},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["vig_desde"] == "2026-04-01"
        assert data["vig_hasta"] == "2026-12-15"
        assert data["estado"] == "inactiva"

    async def test_patch_cohorte_general_fields_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import COHORTE_EDITAR
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/cohortes/{cid}",
            json={
                "nombre": "AGO-2026",
                "anio": 2027,
                "vig_desde": "2026-08-01",
                "vig_hasta": "2027-02-28",
            },
            headers=headers,
        )

        assert resp.status_code == 200
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == COHORTE_EDITAR))
        audit = result.scalar_one()
        assert audit.detalle["cohorte_id"] == cid
        assert audit.detalle["cambios"]["nombre"] == {"anterior": "MAR-2026", "nuevo": "AGO-2026"}
        assert audit.detalle["cambios"]["anio"] == {"anterior": 2026, "nuevo": 2027}
        assert audit.detalle["cambios"]["vig_desde"] == {"anterior": "2026-03-01", "nuevo": "2026-08-01"}
        assert audit.detalle["cambios"]["vig_hasta"] == {"anterior": None, "nuevo": "2027-02-28"}
        assert audit.filas_afectadas == 1

    async def test_patch_cohorte_estado_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import COHORTE_CAMBIAR_ESTADO
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/cohortes/{cid}",
            json={"estado": "inactiva"},
            headers=headers,
        )

        assert resp.status_code == 200
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == COHORTE_CAMBIAR_ESTADO))
        audit = result.scalar_one()
        assert audit.detalle["cohorte_id"] == cid
        assert audit.detalle["carrera_id"] == carrera_id
        assert audit.detalle["nombre"] == "MAR-2026"
        assert audit.detalle["estado_anterior"] == "activa"
        assert audit.detalle["estado_nuevo"] == "inactiva"
        assert audit.filas_afectadas == 1

    async def test_patch_cohorte_without_estado_change_does_not_create_estado_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import COHORTE_CAMBIAR_ESTADO
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/cohortes/{cid}",
            json={"nombre": "MAR-2026 actualizado"},
            headers=headers,
        )

        assert resp.status_code == 200
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == COHORTE_CAMBIAR_ESTADO))
        assert result.scalars().all() == []

    async def test_patch_cohorte_can_clear_vig_hasta(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/cohortes",
            json={
                "carrera_id": carrera_id,
                "nombre": "MAR-2026",
                "anio": 2026,
                "vig_desde": "2026-03-01",
                "vig_hasta": "2026-12-15",
            },
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/cohortes/{cid}",
            json={"vig_hasta": None},
            headers=headers,
        )

        assert resp.status_code == 200
        assert resp.json()["vig_hasta"] is None

    async def test_patch_cohorte_duplicate_name_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        created = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "AGO-2026", "anio": 2026, "vig_desde": "2026-08-01"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/cohortes/{cid}",
            json={"nombre": "MAR-2026"},
            headers=headers,
        )

        assert resp.status_code == 409

    async def test_patch_cohorte_blank_name_returns_422(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/cohortes/{cid}",
            json={"nombre": "   "},
            headers=headers,
        )

        assert resp.status_code == 422

    async def test_patch_cohorte_not_found_returns_404(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = await async_client.patch(f"/api/admin/cohortes/{fake_id}", json={"nombre": "test"}, headers=headers)
        assert resp.status_code == 404

    async def test_delete_cohorte_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import COHORTE_ELIMINAR
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cid = created.json()["id"]

        resp = await async_client.delete(f"/api/admin/cohortes/{cid}", headers=headers)

        assert resp.status_code == 204
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == COHORTE_ELIMINAR))
        audit = result.scalar_one()
        assert audit.detalle["cohorte_id"] == cid
        assert audit.detalle["carrera_id"] == carrera_id
        assert audit.detalle["nombre"] == "MAR-2026"
        assert audit.filas_afectadas == 1

    async def test_cohorte_response_has_activo_and_creada_en(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], carrera_id: str,
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )

        data = resp.json()
        assert data["activo"] is True
        assert data["creada_en"] == data["created_at"]


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

    async def test_create_materia_with_carrera_cohorte_carga_and_estado(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        carrera = await async_client.post("/api/admin/carreras", json={"codigo": "CARR", "nombre": "Carrera"}, headers=headers)
        carrera_id = carrera.json()["id"]
        cohorte = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cohorte_id = cohorte.json()["id"]

        resp = await async_client.post(
            "/api/admin/materias",
            json={
                "codigo": "PROG_I",
                "nombre": "Programacion I",
                "carrera_id": carrera_id,
                "cohorte_id": cohorte_id,
                "carga_horaria": 120,
                "estado": "inactiva",
            },
            headers=headers,
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["carrera_id"] == carrera_id
        assert data["cohorte_id"] == cohorte_id
        assert data["carga_horaria"] == 120
        assert data["estado"] == "inactiva"

    async def test_create_materia_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import MATERIA_CREAR
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "Programacion I", "carga_horaria": 120},
            headers=headers,
        )

        assert resp.status_code == 201
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == MATERIA_CREAR))
        audit = result.scalar_one()
        assert audit.detalle["materia_id"] == resp.json()["id"]
        assert audit.detalle["codigo"] == "PROG_I"
        assert audit.detalle["nombre"] == "Programacion I"
        assert audit.detalle["carga_horaria"] == 120
        assert audit.filas_afectadas == 1

    async def test_create_materia_on_inactive_carrera_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        carrera = await async_client.post("/api/admin/carreras", json={"codigo": "CARR", "nombre": "Carrera"}, headers=headers)
        carrera_id = carrera.json()["id"]
        await async_client.patch(f"/api/admin/carreras/{carrera_id}", json={"estado": "inactiva"}, headers=headers)

        resp = await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "Programacion I", "carrera_id": carrera_id},
            headers=headers,
        )

        assert resp.status_code == 409

    async def test_create_materia_on_inactive_cohorte_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        carrera = await async_client.post("/api/admin/carreras", json={"codigo": "CARR", "nombre": "Carrera"}, headers=headers)
        carrera_id = carrera.json()["id"]
        cohorte = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cohorte_id = cohorte.json()["id"]
        await async_client.patch(f"/api/admin/cohortes/{cohorte_id}", json={"estado": "inactiva"}, headers=headers)

        resp = await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "Programacion I", "carrera_id": carrera_id, "cohorte_id": cohorte_id},
            headers=headers,
        )

        assert resp.status_code == 409

    async def test_create_materia_duplicate_codigo_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "Original"}, headers=headers)
        resp = await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "Duplicate"}, headers=headers)

        assert resp.status_code == 409

    async def test_create_materia_blank_required_fields_returns_422(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/materias",
            json={"codigo": " ", "nombre": "   "},
            headers=headers,
        )

        assert resp.status_code == 422

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
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

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

    async def test_soft_delete_materia_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import MATERIA_ELIMINAR
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/materias", json={"codigo": "DEL", "nombre": "Delete Me"}, headers=headers)
        mid = created.json()["id"]

        delete_resp = await async_client.delete(f"/api/admin/materias/{mid}", headers=headers)

        assert delete_resp.status_code == 204
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == MATERIA_ELIMINAR))
        audit = result.scalar_one()
        assert audit.detalle["materia_id"] == mid
        assert audit.detalle["codigo"] == "DEL"
        assert audit.detalle["nombre"] == "Delete Me"
        assert audit.filas_afectadas == 1

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

    async def test_update_materia_general_fields_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import MATERIA_EDITAR
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "Original", "carga_horaria": 80},
            headers=headers,
        )
        mid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/materias/{mid}",
            json={"codigo": "PROG_1", "nombre": "Updated", "carga_horaria": 120},
            headers=headers,
        )

        assert resp.status_code == 200
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == MATERIA_EDITAR))
        audit = result.scalar_one()
        assert audit.detalle["materia_id"] == mid
        assert audit.detalle["cambios"]["codigo"] == {"anterior": "PROG_I", "nuevo": "PROG_1"}
        assert audit.detalle["cambios"]["nombre"] == {"anterior": "Original", "nuevo": "Updated"}
        assert audit.detalle["cambios"]["carga_horaria"] == {"anterior": 80, "nuevo": 120}
        assert audit.filas_afectadas == 1

    async def test_update_materia_blank_required_fields_returns_422(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "Original"}, headers=headers)
        mid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/materias/{mid}", json={"codigo": " ", "nombre": ""}, headers=headers)

        assert resp.status_code == 422

    async def test_update_materia_estado_creates_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import MATERIA_CAMBIAR_ESTADO
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "Original"}, headers=headers)
        mid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/materias/{mid}", json={"estado": "inactiva"}, headers=headers)

        assert resp.status_code == 200
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == MATERIA_CAMBIAR_ESTADO))
        audit = result.scalar_one()
        assert audit.detalle["materia_id"] == mid
        assert audit.detalle["codigo"] == "PROG_I"
        assert audit.detalle["nombre"] == "Original"
        assert audit.detalle["estado_anterior"] == "activa"
        assert audit.detalle["estado_nuevo"] == "inactiva"
        assert audit.filas_afectadas == 1

    async def test_update_materia_without_estado_change_does_not_create_estado_audit_log(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        from app.models.audit_log import AuditLog
        from app.models.permisos import MATERIA_CAMBIAR_ESTADO
        from sqlalchemy import select

        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/materias", json={"codigo": "PROG_I", "nombre": "Original"}, headers=headers)
        mid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/materias/{mid}", json={"nombre": "Updated"}, headers=headers)

        assert resp.status_code == 200
        result = await db_session.execute(select(AuditLog).where(AuditLog.accion == MATERIA_CAMBIAR_ESTADO))
        assert result.scalars().all() == []

    async def test_materia_response_has_computed_fields(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "Programacion I"},
            headers=headers,
        )

        data = resp.json()
        assert data["activo"] is True
        assert data["creada_en"] == data["created_at"]
        assert data["carrera_id"] is None
        assert data["cohorte_id"] is None
        assert data["carga_horaria"] == 0
        assert data["carrera_nombre"] is None
        assert data["cohorte_nombre"] is None

    async def test_list_materias_filter_by_carrera_and_cohorte(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        carrera_a = await async_client.post("/api/admin/carreras", json={"codigo": "CARR-A", "nombre": "Carrera A"}, headers=headers)
        carrera_a_id = carrera_a.json()["id"]
        carrera_b = await async_client.post("/api/admin/carreras", json={"codigo": "CARR-B", "nombre": "Carrera B"}, headers=headers)
        carrera_b_id = carrera_b.json()["id"]

        cohorte_a = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_a_id, "nombre": "COH-A", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cohorte_a_id = cohorte_a.json()["id"]

        from app.models.estructura_academica import Materia

        m1 = Materia(tenant_id=seed_tenant_admin["tenant_id"], codigo="M1", nombre="Materia 1", carrera_id=UUID(carrera_a_id), cohorte_id=UUID(cohorte_a_id))
        m2 = Materia(tenant_id=seed_tenant_admin["tenant_id"], codigo="M2", nombre="Materia 2", carrera_id=UUID(carrera_b_id))
        db_session.add_all([m1, m2])
        await db_session.commit()

        resp_all = await async_client.get("/api/admin/materias", headers=headers)
        assert resp_all.json()["total"] == 2

        resp_filtered = await async_client.get(f"/api/admin/materias?carrera_id={carrera_a_id}&cohorte_id={cohorte_a_id}", headers=headers)
        assert resp_filtered.status_code == 200
        data = resp_filtered.json()
        assert data["total"] == 1
        assert data["items"][0]["codigo"] == "M1"

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

    # ── Codigo / carga_horaria tests ──────────────────────────

    async def test_update_materia_codigo_and_carga_horaria(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "Original"},
            headers=headers,
        )
        mid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/materias/{mid}",
            json={"codigo": "PROG_II", "carga_horaria": 120},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["codigo"] == "PROG_II"
        assert data["carga_horaria"] == 120

    async def test_update_materia_carrera_and_cohorte(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        carrera = await async_client.post("/api/admin/carreras", json={"codigo": "CARR", "nombre": "Carrera"}, headers=headers)
        carrera_id = carrera.json()["id"]
        cohorte = await async_client.post(
            "/api/admin/cohortes",
            json={"carrera_id": carrera_id, "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01"},
            headers=headers,
        )
        cohorte_id = cohorte.json()["id"]
        created = await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "Original"},
            headers=headers,
        )
        mid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/materias/{mid}",
            json={"carrera_id": carrera_id, "cohorte_id": cohorte_id},
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["carrera_id"] == carrera_id
        assert data["cohorte_id"] == cohorte_id

    async def test_update_materia_duplicate_codigo_returns_409(
        self, estructura_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "First"},
            headers=headers,
        )
        created = await async_client.post(
            "/api/admin/materias",
            json={"codigo": "PROG_II", "nombre": "Second"},
            headers=headers,
        )
        mid = created.json()["id"]

        resp = await async_client.patch(
            f"/api/admin/materias/{mid}",
            json={"codigo": "PROG_I"},
            headers=headers,
        )

        assert resp.status_code == 409


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
            ("PATCH", "/api/admin/cohortes/00000000-0000-0000-0000-000000000000"),
            ("GET", "/api/admin/materias"),
            ("POST", "/api/admin/materias"),
        ]
        for method, url in endpoints:
            if method == "GET":
                resp = await async_client.get(url, headers=headers)
            elif method == "PATCH":
                resp = await async_client.patch(url, json={}, headers=headers)
            else:
                resp = await async_client.post(url, json={}, headers=headers)
            assert resp.status_code == 403, f"{method} {url} expected 403, got {resp.status_code}"
