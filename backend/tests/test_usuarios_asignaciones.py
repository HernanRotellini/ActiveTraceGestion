"""Tests para C-07 Usuarios y Asignaciones.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

from datetime import date, timedelta
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
async def usuarios_schema(db_engine: None):
    """Creates full schema with usuarios and asignaciones tables."""
    from app.core.database import get_sessionmaker
    from app.models.usuarios_asignaciones import Asignacion, Usuario  # noqa: F401
    from app.services.auth import login_rate_limiter

    login_rate_limiter.reset_all()

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS asignaciones, usuarios, cohortes, carreras, materias, "
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
    """Seeds tenant + admin user + usuarios:gestionar + equipos:asignar permissions."""
    tenant = Tenant(name="Tenant test-tenant", code="test-tenant")
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
    for codigo, nombre, modulo, accion in [
        ("usuarios:gestionar", "Gestionar usuarios", "usuarios", "gestionar"),
        ("equipos:asignar", "Asignar equipos", "equipos", "asignar"),
    ]:
        permiso = Permiso(
            tenant_id=tenant.id,
            codigo=codigo,
            nombre=nombre,
            modulo=modulo,
            accion=accion,
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


async def login(client: AsyncClient, tenant_code: str = "test-tenant", email: str = "admin@test.com") -> dict[str, Any]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": "password"},
    )
    return resp.json()


async def admin_headers(client: AsyncClient, tenant_code: str = "test-tenant", email: str = "admin@test.com") -> dict[str, str]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": "password"},
    )
    data = resp.json()
    assert "access_token" in data, f"Login failed for {email}@{tenant_code}: {data}"
    return {"Authorization": f"Bearer {data['access_token']}"}


# ═══════════════════════════════════════════════════════════════
# 7.1 — Usuario CRUD
# ═══════════════════════════════════════════════════════════════


class TestUsuarioCRUD:
    """RED → GREEN: Usuario CRUD operations."""

    USUARIO_PAYLOAD = {
        "nombre": "Juan",
        "apellidos": "Perez",
        "email": "juan@example.com",
        "dni": "12345678",
        "cuil": "20-12345678-9",
        "cbu": "00000031000000000001",
        "alias_cbu": "JUAN.PEREZ.ALIAS",
    }

    async def test_create_usuario_returns_201_with_estado_activo(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.post(
            "/api/admin/usuarios",
            json=self.USUARIO_PAYLOAD,
            headers=headers,
        )

        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "Juan"
        assert data["apellidos"] == "Perez"
        assert data["email"] == "juan@example.com"
        assert data["dni"] == "12345678"
        assert data["estado"] == "activo"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_usuario_duplicate_email_returns_409(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post("/api/admin/usuarios", json=self.USUARIO_PAYLOAD, headers=headers)
        resp = await async_client.post("/api/admin/usuarios", json=self.USUARIO_PAYLOAD, headers=headers)

        assert resp.status_code == 409

    async def test_same_email_different_tenant_succeeds(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        t2 = Tenant(name="Tenant t2", code="t2")
        db_session.add(t2)
        await db_session.flush()
        u2 = AuthUser(
            tenant_id=t2.id, email="admin2@test.com",
            password_hash=hash_password("password"), roles=["ADMIN"], is_active=True,
        )
        db_session.add(u2)
        from app.models.rbac import Permiso, Rol, RolPermiso
        r2 = Rol(tenant_id=t2.id, codigo="ADMIN", nombre="Admin")
        db_session.add(r2)
        for codigo in ("usuarios:gestionar", "equipos:asignar"):
            p = Permiso(tenant_id=t2.id, codigo=codigo, nombre=codigo, modulo=codigo.split(":")[0], accion=codigo.split(":")[1])
            db_session.add(p)
            await db_session.flush()
            db_session.add(RolPermiso(tenant_id=t2.id, rol_id=r2.id, permiso_id=p.id, habilitado=True, alcance="global"))
        await db_session.commit()

        h1 = await admin_headers(async_client)
        r1 = await async_client.post("/api/admin/usuarios", json=self.USUARIO_PAYLOAD, headers=h1)
        assert r1.status_code == 201

        h2 = await admin_headers(async_client, "t2", "admin2@test.com")
        r2 = await async_client.post("/api/admin/usuarios", json=self.USUARIO_PAYLOAD, headers=h2)
        assert r2.status_code == 201

    async def test_list_usuarios_returns_tenant_scoped(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        await async_client.post("/api/admin/usuarios", json=self.USUARIO_PAYLOAD, headers=headers)
        await async_client.post("/api/admin/usuarios", json={**self.USUARIO_PAYLOAD, "email": "maria@example.com", "nombre": "Maria"}, headers=headers)

        resp = await async_client.get("/api/admin/usuarios", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        emails = {u["email"] for u in data}
        assert emails == {"juan@example.com", "maria@example.com"}

    async def test_get_usuario_by_id(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/usuarios", json=self.USUARIO_PAYLOAD, headers=headers)
        uid = created.json()["id"]

        resp = await async_client.get(f"/api/admin/usuarios/{uid}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "juan@example.com"

    async def test_get_usuario_not_found_returns_404(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        resp = await async_client.get("/api/admin/usuarios/00000000-0000-0000-0000-000000000000", headers=headers)
        assert resp.status_code == 404

    async def test_update_usuario_fields(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/usuarios", json=self.USUARIO_PAYLOAD, headers=headers)
        uid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/usuarios/{uid}", json={"nombre": "Juan Carlos"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Juan Carlos"

    async def test_toggle_usuario_to_inactivo(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/usuarios", json=self.USUARIO_PAYLOAD, headers=headers)
        uid = created.json()["id"]

        resp = await async_client.patch(f"/api/admin/usuarios/{uid}", json={"estado": "inactivo"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["estado"] == "inactivo"

    async def test_soft_delete_usuario(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        created = await async_client.post("/api/admin/usuarios", json=self.USUARIO_PAYLOAD, headers=headers)
        uid = created.json()["id"]

        delete_resp = await async_client.delete(f"/api/admin/usuarios/{uid}", headers=headers)
        assert delete_resp.status_code == 204

        get_resp = await async_client.get(f"/api/admin/usuarios/{uid}", headers=headers)
        assert get_resp.status_code == 404

    async def test_tenant_a_cannot_see_tenant_b_usuarios(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        t2 = Tenant(name="Tenant t2", code="t2")
        db_session.add(t2)
        await db_session.flush()
        u2 = AuthUser(tenant_id=t2.id, email="admin2@test.com", password_hash=hash_password("password"), roles=["ADMIN"], is_active=True)
        db_session.add(u2)
        from app.models.rbac import Permiso, Rol, RolPermiso
        r2 = Rol(tenant_id=t2.id, codigo="ADMIN", nombre="Admin")
        db_session.add(r2)
        for codigo in ("usuarios:gestionar", "equipos:asignar"):
            p = Permiso(tenant_id=t2.id, codigo=codigo, nombre=codigo, modulo=codigo.split(":")[0], accion=codigo.split(":")[1])
            db_session.add(p)
            await db_session.flush()
            db_session.add(RolPermiso(tenant_id=t2.id, rol_id=r2.id, permiso_id=p.id, habilitado=True, alcance="global"))
        await db_session.commit()

        h1 = await admin_headers(async_client)
        h2 = await admin_headers(async_client, "t2", "admin2@test.com")

        await async_client.post("/api/admin/usuarios", json={**self.USUARIO_PAYLOAD, "email": "t1@test.com"}, headers=h1)
        await async_client.post("/api/admin/usuarios", json={**self.USUARIO_PAYLOAD, "email": "t2@test.com"}, headers=h2)

        resp = await async_client.get("/api/admin/usuarios", headers=h1)
        emails = [u["email"] for u in resp.json()]
        assert "t1@test.com" in emails
        assert "t2@test.com" not in emails

    async def test_tenant_a_cannot_update_tenant_b_usuario(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        t2 = Tenant(name="Tenant t2", code="t2")
        db_session.add(t2)
        await db_session.flush()
        u2 = AuthUser(tenant_id=t2.id, email="admin2@test.com", password_hash=hash_password("password"), roles=["ADMIN"], is_active=True)
        db_session.add(u2)
        from app.models.rbac import Permiso, Rol, RolPermiso
        r2 = Rol(tenant_id=t2.id, codigo="ADMIN", nombre="Admin")
        db_session.add(r2)
        for codigo in ("usuarios:gestionar", "equipos:asignar"):
            p = Permiso(tenant_id=t2.id, codigo=codigo, nombre=codigo, modulo=codigo.split(":")[0], accion=codigo.split(":")[1])
            db_session.add(p)
            await db_session.flush()
            db_session.add(RolPermiso(tenant_id=t2.id, rol_id=r2.id, permiso_id=p.id, habilitado=True, alcance="global"))
        await db_session.commit()

        h2 = await admin_headers(async_client, "t2", "admin2@test.com")
        created = await async_client.post("/api/admin/usuarios", json={**self.USUARIO_PAYLOAD, "email": "t2@test.com"}, headers=h2)
        uid = created.json()["id"]

        h1 = await admin_headers(async_client)
        resp = await async_client.patch(f"/api/admin/usuarios/{uid}", json={"nombre": "Hacked"}, headers=h1)
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
# 7.2 — PII Encryption
# ═══════════════════════════════════════════════════════════════


class TestPIIEncryption:
    """RED → GREEN: PII fields are encrypted at rest."""

    async def test_pii_stored_as_ciphertext_in_db(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        payload = {
            "nombre": "Juan",
            "apellidos": "Perez",
            "email": "juan@example.com",
            "dni": "12345678",
            "cuil": "20-12345678-9",
        }
        resp = await async_client.post("/api/admin/usuarios", json=payload, headers=headers)
        assert resp.status_code == 201

        from app.models.usuarios_asignaciones import Usuario
        result = await db_session.execute(
            text("SELECT email, dni, cuil FROM usuarios")
        )
        row = result.one()
        assert row.email != "juan@example.com"
        assert row.dni != "12345678"
        assert row.cuil != "20-12345678-9"
        assert row.email is not None
        assert row.dni is not None
        assert row.cuil is not None

    async def test_pii_returned_as_plaintext_in_response(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)
        payload = {
            "nombre": "Maria",
            "apellidos": "Gomez",
            "email": "maria@example.com",
            "dni": "87654321",
        }
        created = await async_client.post("/api/admin/usuarios", json=payload, headers=headers)
        uid = created.json()["id"]

        resp = await async_client.get(f"/api/admin/usuarios/{uid}", headers=headers)
        assert resp.json()["email"] == "maria@example.com"
        assert resp.json()["dni"] == "87654321"


# ═══════════════════════════════════════════════════════════════
# 7.3 — Asignacion CRUD
# ═══════════════════════════════════════════════════════════════


class TestAsignacionCRUD:
    """RED → GREEN: Asignacion CRUD operations."""

    @pytest.fixture
    async def seed_academic_context(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> dict[str, Any]:
        from app.models.estructura_academica import Carrera, Cohorte, Materia

        headers = await admin_headers(async_client)

        tenant_id = seed_tenant_admin["tenant_id"]

        carrera = Carrera(tenant_id=tenant_id, codigo="TUPAD", nombre="Tecnicatura")
        db_session.add(carrera)
        await db_session.flush()

        cohorte = Cohorte(tenant_id=tenant_id, carrera_id=carrera.id, nombre="MAR-2026", anio=2026, vig_desde=date(2026, 3, 1))
        db_session.add(cohorte)
        await db_session.flush()

        materia = Materia(tenant_id=tenant_id, codigo="PROG_I", nombre="Programacion I")
        db_session.add(materia)
        await db_session.flush()

        usuario = await async_client.post("/api/admin/usuarios", json={
            "nombre": "Pedro", "apellidos": "Lopez", "email": "pedro@test.com",
        }, headers=headers)
        usuario_id = usuario.json()["id"]

        await db_session.commit()

        return {
            "carrera_id": str(carrera.id),
            "cohorte_id": str(cohorte.id),
            "materia_id": str(materia.id),
            "usuario_id": usuario_id,
            "headers": headers,
        }

    async def test_create_asignacion_with_full_context(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_academic_context: dict[str, Any],
    ) -> None:
        ctx = seed_academic_context
        headers = ctx["headers"]

        resp = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"],
            "rol": "PROFESOR",
            "materia_id": ctx["materia_id"],
            "carrera_id": ctx["carrera_id"],
            "cohorte_id": ctx["cohorte_id"],
            "comisiones": ["A", "B"],
            "desde": "2026-03-01",
            "hasta": "2026-12-31",
        }, headers=headers)

        assert resp.status_code == 201
        data = resp.json()
        assert data["rol"] == "PROFESOR"
        assert data["materia_id"] == ctx["materia_id"]
        assert data["comisiones"] == ["A", "B"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_asignacion_global_role(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_academic_context: dict[str, Any],
    ) -> None:
        ctx = seed_academic_context
        headers = ctx["headers"]

        resp = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"],
            "rol": "ADMIN",
            "desde": "2026-01-01",
        }, headers=headers)

        assert resp.status_code == 201
        assert resp.json()["rol"] == "ADMIN"
        assert resp.json()["materia_id"] is None

    async def test_create_asignacion_with_responsable(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_academic_context: dict[str, Any],
    ) -> None:
        ctx = seed_academic_context
        headers = ctx["headers"]

        r2 = await async_client.post("/api/admin/usuarios", json={
            "nombre": "Jefe", "apellidos": "Responsable", "email": "jefe@test.com",
        }, headers=headers)
        responsable_id = r2.json()["id"]

        resp = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"],
            "rol": "PROFESOR",
            "responsable_id": responsable_id,
            "materia_id": ctx["materia_id"],
            "desde": "2026-03-01",
        }, headers=headers)

        assert resp.status_code == 201
        assert resp.json()["responsable_id"] == responsable_id

    async def test_list_asignaciones(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_academic_context: dict[str, Any],
    ) -> None:
        ctx = seed_academic_context
        headers = ctx["headers"]

        await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"], "rol": "PROFESOR",
            "materia_id": ctx["materia_id"], "desde": "2026-03-01",
        }, headers=headers)
        await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"], "rol": "COORDINADOR",
            "materia_id": ctx["materia_id"], "desde": "2026-03-01",
        }, headers=headers)

        resp = await async_client.get("/api/asignaciones", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_filter_asignaciones_by_materia(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_academic_context: dict[str, Any],
    ) -> None:
        ctx = seed_academic_context
        headers = ctx["headers"]

        from app.models.estructura_academica import Materia
        m2 = Materia(tenant_id=seed_tenant_admin["tenant_id"], codigo="PROG_II", nombre="Programacion II")
        db_session.add(m2)
        await db_session.flush()
        await db_session.commit()

        await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"], "rol": "PROFESOR",
            "materia_id": ctx["materia_id"], "desde": "2026-03-01",
        }, headers=headers)
        await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"], "rol": "PROFESOR",
            "materia_id": str(m2.id), "desde": "2026-03-01",
        }, headers=headers)

        resp = await async_client.get(f"/api/asignaciones?materia_id={ctx['materia_id']}", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["materia_id"] == ctx["materia_id"]

    async def test_get_asignacion_by_id(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_academic_context: dict[str, Any],
    ) -> None:
        ctx = seed_academic_context
        headers = ctx["headers"]

        created = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"], "rol": "PROFESOR",
            "materia_id": ctx["materia_id"], "desde": "2026-03-01",
        }, headers=headers)
        aid = created.json()["id"]

        resp = await async_client.get(f"/api/asignaciones/{aid}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["rol"] == "PROFESOR"

    async def test_soft_delete_asignacion(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_academic_context: dict[str, Any],
    ) -> None:
        ctx = seed_academic_context
        headers = ctx["headers"]

        created = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"], "rol": "PROFESOR",
            "materia_id": ctx["materia_id"], "desde": "2026-03-01",
        }, headers=headers)
        aid = created.json()["id"]

        delete_resp = await async_client.delete(f"/api/asignaciones/{aid}", headers=headers)
        assert delete_resp.status_code == 204

        get_resp = await async_client.get(f"/api/asignaciones/{aid}", headers=headers)
        assert get_resp.status_code == 404


# ═══════════════════════════════════════════════════════════════
# 7.4 — Vigencia
# ═══════════════════════════════════════════════════════════════


class TestVigencia:
    """RED → GREEN: estado_vigencia computation."""

    @pytest.fixture
    async def seed_context(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> dict[str, Any]:
        headers = await admin_headers(async_client)
        usuario = await async_client.post("/api/admin/usuarios", json={
            "nombre": "Test", "apellidos": "User", "email": "test@test.com",
        }, headers=headers)
        return {"usuario_id": usuario.json()["id"], "headers": headers}

    async def test_expired_assignment_shows_vencida(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_context: dict[str, Any],
    ) -> None:
        ctx = seed_context
        headers = ctx["headers"]

        last_year = (date.today() - timedelta(days=400)).isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        resp = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"],
            "rol": "PROFESOR",
            "desde": last_year,
            "hasta": yesterday,
        }, headers=headers)

        assert resp.status_code == 201
        assert resp.json()["estado_vigencia"] == "vencida"

    async def test_active_assignment_shows_vigente(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_context: dict[str, Any],
    ) -> None:
        ctx = seed_context
        headers = ctx["headers"]

        last_year = (date.today() - timedelta(days=365)).isoformat()
        next_year = (date.today() + timedelta(days=365)).isoformat()

        resp = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"],
            "rol": "PROFESOR",
            "desde": last_year,
            "hasta": next_year,
        }, headers=headers)

        assert resp.status_code == 201
        assert resp.json()["estado_vigencia"] == "vigente"

    async def test_active_no_end_date_shows_vigente(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_context: dict[str, Any],
    ) -> None:
        ctx = seed_context
        headers = ctx["headers"]

        last_year = (date.today() - timedelta(days=30)).isoformat()

        resp = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"],
            "rol": "PROFESOR",
            "desde": last_year,
        }, headers=headers)

        assert resp.status_code == 201
        assert resp.json()["estado_vigencia"] == "vigente"


# ═══════════════════════════════════════════════════════════════
# 7.5 — Multi-rol support
# ═══════════════════════════════════════════════════════════════


class TestMultiRol:
    """RED → GREEN: Single usuario with multiple roles."""

    @pytest.fixture
    async def seed_context(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> dict[str, Any]:
        headers = await admin_headers(async_client)
        from app.models.estructura_academica import Materia
        t = seed_tenant_admin["tenant_id"]
        m1 = Materia(tenant_id=t, codigo="M1", nombre="Materia1")
        m2 = Materia(tenant_id=t, codigo="M2", nombre="Materia2")
        db_session.add_all([m1, m2])
        await db_session.flush()
        await db_session.commit()
        usuario = await async_client.post("/api/admin/usuarios", json={
            "nombre": "Multi", "apellidos": "Rol", "email": "multi@test.com",
        }, headers=headers)
        return {
            "usuario_id": usuario.json()["id"],
            "materia1_id": str(m1.id),
            "materia2_id": str(m2.id),
            "headers": headers,
        }

    async def test_user_holds_profesor_and_coordinador(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any], seed_context: dict[str, Any],
    ) -> None:
        ctx = seed_context
        headers = ctx["headers"]

        r1 = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"], "rol": "PROFESOR",
            "materia_id": ctx["materia1_id"], "desde": "2026-03-01",
        }, headers=headers)
        assert r1.status_code == 201

        r2 = await async_client.post("/api/asignaciones", json={
            "usuario_id": ctx["usuario_id"], "rol": "COORDINADOR",
            "materia_id": ctx["materia2_id"], "desde": "2026-03-01",
        }, headers=headers)
        assert r2.status_code == 201

        resp = await async_client.get(f"/api/asignaciones?usuario_id={ctx['usuario_id']}", headers=headers)
        assert resp.status_code == 200
        roles = {a["rol"] for a in resp.json()}
        assert roles == {"PROFESOR", "COORDINADOR"}


# ═══════════════════════════════════════════════════════════════
# 7.6 — Authorization guards
# ═══════════════════════════════════════════════════════════════


class TestAuthGuardUsuarios:
    """All usuario endpoints require usuarios:gestionar → 403 without it."""

    async def test_endpoints_return_403_without_usuarios_gestionar(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
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
        headers = {"Authorization": f"Bearer {data['access_token']}"}

        endpoints = [
            ("GET", "/api/admin/usuarios"),
            ("POST", "/api/admin/usuarios"),
            ("GET", f"/api/admin/usuarios/{'00000000-0000-0000-0000-000000000000'}"),
            ("PATCH", f"/api/admin/usuarios/{'00000000-0000-0000-0000-000000000000'}"),
            ("DELETE", f"/api/admin/usuarios/{'00000000-0000-0000-0000-000000000000'}"),
        ]
        for method, url in endpoints:
            if method == "GET":
                resp = await async_client.get(url, headers=headers)
            elif method == "POST":
                resp = await async_client.post(url, json={}, headers=headers)
            elif method == "PATCH":
                resp = await async_client.patch(url, json={}, headers=headers)
            elif method == "DELETE":
                resp = await async_client.delete(url, headers=headers)
            assert resp.status_code == 403, f"{method} {url} expected 403, got {resp.status_code}"


class TestAuthGuardAsignaciones:
    """All asignacion endpoints require equipos:asignar → 403 without it."""

    async def test_endpoints_return_403_without_equipos_asignar(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
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
        headers = {"Authorization": f"Bearer {data['access_token']}"}

        endpoints = [
            ("GET", "/api/asignaciones"),
            ("POST", "/api/asignaciones"),
            ("GET", f"/api/asignaciones/{'00000000-0000-0000-0000-000000000000'}"),
            ("PATCH", f"/api/asignaciones/{'00000000-0000-0000-0000-000000000000'}"),
            ("DELETE", f"/api/asignaciones/{'00000000-0000-0000-0000-000000000000'}"),
        ]
        for method, url in endpoints:
            if method == "GET":
                resp = await async_client.get(url, headers=headers)
            elif method == "POST":
                resp = await async_client.post(url, json={"usuario_id": "00000000-0000-0000-0000-000000000000", "rol": "TEST", "desde": "2026-01-01"}, headers=headers)
            elif method == "PATCH":
                resp = await async_client.patch(url, json={}, headers=headers)
            elif method == "DELETE":
                resp = await async_client.delete(url, headers=headers)
            assert resp.status_code == 403, f"{method} {url} expected 403, got {resp.status_code}"
