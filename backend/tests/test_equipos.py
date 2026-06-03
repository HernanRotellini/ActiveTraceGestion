"""Tests para C-08 Equipos Docentes.

Strict TDD: RED → GREEN → TRIANGULATE → REFACTOR.
"""

from datetime import date, timedelta
from typing import Any

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
    """Creates full schema with all tables."""
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


async def admin_headers(client: AsyncClient, tenant_code: str = "test-tenant", email: str = "admin@test.com") -> dict[str, str]:
    resp = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": "password"},
    )
    data = resp.json()
    assert "access_token" in data, f"Login failed for {email}@{tenant_code}: {data}"
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.fixture
async def seed_equipo_context(
    usuarios_schema,
    db_session: AsyncSession,
    async_client: AsyncClient,
    seed_tenant_admin: dict[str, Any],
) -> dict[str, Any]:
    """Seeds academic context + Usuario matching AuthUser + Usuario for other docente + asignaciones."""
    headers = await admin_headers(async_client)

    tenant_id = seed_tenant_admin["tenant_id"]
    admin_user_id = seed_tenant_admin["user_id"]

    from app.models.estructura_academica import Carrera, Cohorte, Materia
    from app.models.usuarios_asignaciones import Usuario

    carrera = Carrera(tenant_id=tenant_id, codigo="TUPAD", nombre="Tecnicatura")
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(tenant_id=tenant_id, carrera_id=carrera.id, nombre="MAR-2026", anio=2026, vig_desde=date(2026, 3, 1))
    db_session.add(cohorte)
    await db_session.flush()

    materia = Materia(tenant_id=tenant_id, codigo="PROG_I", nombre="Programacion I")
    db_session.add(materia)
    await db_session.flush()

    materia2 = Materia(tenant_id=tenant_id, codigo="PROG_II", nombre="Programacion II")
    db_session.add(materia2)
    await db_session.flush()

    usuario_admin = Usuario(
        id=admin_user_id,
        tenant_id=tenant_id,
        nombre="Admin", apellidos="User", email="admin@test.com",
    )
    db_session.add(usuario_admin)
    await db_session.flush()

    usuario2 = Usuario(
        tenant_id=tenant_id,
        nombre="Maria", apellidos="Garcia", email="maria@test.com",
    )
    db_session.add(usuario2)
    await db_session.flush()

    await db_session.commit()

    return {
        "tenant_id": tenant_id,
        "carrera_id": str(carrera.id),
        "cohorte_id": str(cohorte.id),
        "materia_id": str(materia.id),
        "materia2_id": str(materia2.id),
        "usuario1_id": str(admin_user_id),
        "usuario2_id": str(usuario2.id),
        "headers": headers,
    }


@pytest.fixture
async def seed_asignaciones(
    seed_equipo_context: dict[str, Any],
    async_client: AsyncClient,
) -> dict[str, Any]:
    """Seeds 3 asignaciones on top of seed_equipo_context."""
    ctx = seed_equipo_context
    headers = ctx["headers"]
    today = date.today()

    r1 = await async_client.post("/api/asignaciones", json={
        "usuario_id": ctx["usuario1_id"],
        "rol": "PROFESOR",
        "materia_id": ctx["materia_id"],
        "carrera_id": ctx["carrera_id"],
        "cohorte_id": ctx["cohorte_id"],
        "comisiones": ["A", "B"],
        "desde": (today - timedelta(days=30)).isoformat(),
        "hasta": (today + timedelta(days=300)).isoformat(),
    }, headers=headers)
    vigente_id = r1.json()["id"]

    r2 = await async_client.post("/api/asignaciones", json={
        "usuario_id": ctx["usuario1_id"],
        "rol": "PROFESOR",
        "materia_id": ctx["materia_id"],
        "carrera_id": ctx["carrera_id"],
        "cohorte_id": ctx["cohorte_id"],
        "desde": (today - timedelta(days=400)).isoformat(),
        "hasta": (today - timedelta(days=1)).isoformat(),
    }, headers=headers)
    vencida_id = r2.json()["id"]

    r3 = await async_client.post("/api/asignaciones", json={
        "usuario_id": ctx["usuario1_id"],
        "rol": "PROFESOR",
        "materia_id": ctx["materia2_id"],
        "carrera_id": ctx["carrera_id"],
        "cohorte_id": ctx["cohorte_id"],
        "desde": (today - timedelta(days=30)).isoformat(),
        "hasta": (today + timedelta(days=300)).isoformat(),
    }, headers=headers)
    otra_materia_id = r3.json()["id"]

    r4 = await async_client.post("/api/asignaciones", json={
        "usuario_id": ctx["usuario2_id"],
        "rol": "TUTOR",
        "materia_id": ctx["materia_id"],
        "carrera_id": ctx["carrera_id"],
        "cohorte_id": ctx["cohorte_id"],
        "desde": (today - timedelta(days=30)).isoformat(),
        "hasta": (today + timedelta(days=300)).isoformat(),
    }, headers=headers)
    tutor_id = r4.json()["id"]

    return {
        **ctx,
        "vigente_id": vigente_id,
        "vencida_id": vencida_id,
        "otra_materia_id": otra_materia_id,
        "tutor_id": tutor_id,
    }


# ═══════════════════════════════════════════════════════════════
# 4.1 — Mis Equipos
# ═══════════════════════════════════════════════════════════════


class TestMisEquipos:
    """RED → GREEN: GET /api/equipos/mis-equipos."""

    async def test_docente_ve_sus_asignaciones(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_asignaciones: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.get("/api/equipos/mis-equipos", headers=headers)

        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    async def test_filtra_por_estado_vigente(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_asignaciones: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.get("/api/equipos/mis-equipos?estado=vigente", headers=headers)

        assert resp.status_code == 200
        data = resp.json()
        assert all(a["estado_vigencia"] == "vigente" for a in data)
        assert len(data) == 2

    async def test_filtra_por_materia(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_asignaciones: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.get(
            f"/api/equipos/mis-equipos?materia_id={seed_asignaciones['materia_id']}",
            headers=headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert all(a["materia_id"] == seed_asignaciones["materia_id"] for a in data)
        assert len(data) == 2

    async def test_otro_tenant_no_ve_datos(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_asignaciones: dict[str, Any],
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

        h2 = await admin_headers(async_client, "t2", "admin2@test.com")
        resp = await async_client.get("/api/equipos/mis-equipos", headers=h2)
        assert resp.status_code == 200
        assert len(resp.json()) == 0


# ═══════════════════════════════════════════════════════════════
# 4.2 — Asignación Masiva
# ═══════════════════════════════════════════════════════════════


class TestAsignacionMasiva:
    """RED → GREEN: POST /api/equipos/asignacion-masiva."""

    async def test_crea_todos_los_usuarios(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_equipo_context: dict[str, Any],
    ) -> None:
        ctx = seed_equipo_context
        headers = ctx["headers"]

        payload = {
            "usuario_ids": [ctx["usuario1_id"], ctx["usuario2_id"]],
            "materia_id": ctx["materia_id"],
            "carrera_id": ctx["carrera_id"],
            "cohorte_id": ctx["cohorte_id"],
            "rol": "PROFESOR",
            "desde": "2026-03-01",
            "hasta": "2026-12-31",
        }

        resp = await async_client.post("/api/equipos/asignacion-masiva", json=payload, headers=headers)

        assert resp.status_code == 201
        data = resp.json()
        assert len(data) == 2
        uids = {a["usuario_id"] for a in data}
        assert uids == {ctx["usuario1_id"], ctx["usuario2_id"]}
        for a in data:
            assert a["rol"] == "PROFESOR"
            assert a["materia_id"] == ctx["materia_id"]

    async def test_usuario_inexistente_retorna_404(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_equipo_context: dict[str, Any],
    ) -> None:
        ctx = seed_equipo_context
        headers = ctx["headers"]
        fake_id = "00000000-0000-0000-0000-000000000000"

        payload = {
            "usuario_ids": [ctx["usuario1_id"], fake_id],
            "materia_id": ctx["materia_id"],
            "carrera_id": ctx["carrera_id"],
            "cohorte_id": ctx["cohorte_id"],
            "rol": "PROFESOR",
            "desde": "2026-03-01",
            "hasta": "2026-12-31",
        }

        resp = await async_client.post("/api/equipos/asignacion-masiva", json=payload, headers=headers)

        assert resp.status_code == 404

        get_resp = await async_client.get("/api/asignaciones", headers=headers)
        assert len(get_resp.json()) == 0

    async def test_sin_permiso_retorna_403(
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
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        payload = {
            "usuario_ids": ["00000000-0000-0000-0000-000000000000"],
            "materia_id": "00000000-0000-0000-0000-000000000000",
            "carrera_id": "00000000-0000-0000-0000-000000000000",
            "cohorte_id": "00000000-0000-0000-0000-000000000000",
            "rol": "PROFESOR",
            "desde": "2026-03-01",
        }

        resp = await async_client.post("/api/equipos/asignacion-masiva", json=payload, headers=headers)
        assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════
# 4.3 — Clonar Equipo
# ═══════════════════════════════════════════════════════════════


class TestClonarEquipo:
    """RED → GREEN: POST /api/equipos/clonar."""

    @pytest.fixture
    async def seed_clonar_context(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_tenant_admin: dict[str, Any],
    ) -> dict[str, Any]:
        headers = await admin_headers(async_client)
        tenant_id = seed_tenant_admin["tenant_id"]

        from app.models.estructura_academica import Carrera, Cohorte, Materia

        materia = Materia(tenant_id=tenant_id, codigo="MATE", nombre="Matematicas")
        db_session.add(materia)
        c1 = Carrera(tenant_id=tenant_id, codigo="C1", nombre="Carrera1")
        db_session.add(c1)
        c2 = Carrera(tenant_id=tenant_id, codigo="C2", nombre="Carrera2")
        db_session.add(c2)
        await db_session.flush()
        coh1 = Cohorte(tenant_id=tenant_id, carrera_id=c1.id, nombre="MAR-2026", anio=2026, vig_desde=date(2026, 3, 1))
        db_session.add(coh1)
        coh2 = Cohorte(tenant_id=tenant_id, carrera_id=c2.id, nombre="MAR-2027", anio=2027, vig_desde=date(2027, 3, 1))
        db_session.add(coh2)
        await db_session.flush()
        await db_session.commit()

        r1 = await async_client.post("/api/admin/usuarios", json={
            "nombre": "Clone", "apellidos": "User", "email": "clone@test.com",
        }, headers=headers)
        uid = r1.json()["id"]

        r2 = await async_client.post("/api/admin/usuarios", json={
            "nombre": "Second", "apellidos": "User", "email": "second@test.com",
        }, headers=headers)
        uid2 = r2.json()["id"]

        await async_client.post("/api/asignaciones", json={
            "usuario_id": uid, "rol": "PROFESOR",
            "materia_id": str(materia.id), "carrera_id": str(c1.id), "cohorte_id": str(coh1.id),
            "desde": "2026-03-01", "hasta": "2026-12-31",
        }, headers=headers)

        await async_client.post("/api/asignaciones", json={
            "usuario_id": uid2, "rol": "TUTOR",
            "materia_id": str(materia.id), "carrera_id": str(c1.id), "cohorte_id": str(coh1.id),
            "desde": "2026-03-01", "hasta": "2026-12-31",
        }, headers=headers)

        return {
            "tenant_id": seed_tenant_admin["tenant_id"],
            "materia_id": str(materia.id),
            "origen_carrera_id": str(c1.id),
            "origen_cohorte_id": str(coh1.id),
            "destino_carrera_id": str(c2.id),
            "destino_cohorte_id": str(coh2.id),
            "headers": headers,
        }

    async def test_clonar_exitoso_con_fechas_correctas(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_clonar_context: dict[str, Any],
    ) -> None:
        ctx = seed_clonar_context
        headers = ctx["headers"]

        payload = {
            "origen": {
                "materia_id": ctx["materia_id"],
                "carrera_id": ctx["origen_carrera_id"],
                "cohorte_id": ctx["origen_cohorte_id"],
            },
            "destino": {
                "carrera_id": ctx["destino_carrera_id"],
                "cohorte_id": ctx["destino_cohorte_id"],
                "desde": "2027-03-01",
                "hasta": "2027-12-31",
            },
        }

        resp = await async_client.post("/api/equipos/clonar", json=payload, headers=headers)

        assert resp.status_code == 201
        data = resp.json()
        assert len(data) == 2
        for a in data:
            assert a["desde"] == "2027-03-01"
            assert a["hasta"] == "2027-12-31"
            assert a["carrera_id"] == ctx["destino_carrera_id"]
            assert a["cohorte_id"] == ctx["destino_cohorte_id"]
            assert a["materia_id"] == ctx["materia_id"]

    async def test_clonar_origen_sin_asignaciones_retorna_lista_vacia(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_clonar_context: dict[str, Any],
    ) -> None:
        ctx = seed_clonar_context
        headers = ctx["headers"]

        from app.models.estructura_academica import Carrera, Cohorte
        c3 = Carrera(tenant_id=ctx["tenant_id"], codigo="C3", nombre="Carrera3")
        db_session.add(c3)
        await db_session.flush()
        coh3 = Cohorte(tenant_id=ctx["tenant_id"], carrera_id=c3.id, nombre="MAR-2028", anio=2028, vig_desde=date(2028, 3, 1))
        db_session.add(coh3)
        await db_session.commit()

        payload = {
            "origen": {
                "materia_id": ctx["materia_id"],
                "carrera_id": str(c3.id),
                "cohorte_id": str(coh3.id),
            },
            "destino": {
                "carrera_id": ctx["destino_carrera_id"],
                "cohorte_id": ctx["destino_cohorte_id"],
                "desde": "2027-03-01",
            },
        }

        resp = await async_client.post("/api/equipos/clonar", json=payload, headers=headers)

        assert resp.status_code == 201
        assert resp.json() == []

    async def test_clonar_sin_permiso_retorna_403(
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
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        payload = {
            "origen": {"materia_id": "00000000-0000-0000-0000-000000000000", "carrera_id": "00000000-0000-0000-0000-000000000000", "cohorte_id": "00000000-0000-0000-0000-000000000000"},
            "destino": {"carrera_id": "00000000-0000-0000-0000-000000000000", "cohorte_id": "00000000-0000-0000-0000-000000000000", "desde": "2026-03-01"},
        }
        resp = await async_client.post("/api/equipos/clonar", json=payload, headers=headers)
        assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════
# 4.4 — Vigencia General
# ═══════════════════════════════════════════════════════════════


class TestVigenciaEquipo:
    """RED → GREEN: PATCH /api/equipos/vigencia."""

    @pytest.fixture
    async def seed_vigencia_context(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_equipo_context: dict[str, Any],
    ) -> dict[str, Any]:
        ctx = seed_equipo_context
        headers = ctx["headers"]

        for uid in [ctx["usuario1_id"], ctx["usuario2_id"]]:
            await async_client.post("/api/asignaciones", json={
                "usuario_id": uid,
                "rol": "PROFESOR",
                "materia_id": ctx["materia_id"],
                "carrera_id": ctx["carrera_id"],
                "cohorte_id": ctx["cohorte_id"],
                "desde": "2026-03-01",
                "hasta": "2026-12-31",
            }, headers=headers)

        return ctx

    async def test_update_ambos_campos(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_vigencia_context: dict[str, Any],
    ) -> None:
        ctx = seed_vigencia_context
        headers = ctx["headers"]

        payload = {
            "materia_id": ctx["materia_id"],
            "carrera_id": ctx["carrera_id"],
            "cohorte_id": ctx["cohorte_id"],
            "desde": "2026-04-01",
            "hasta": "2027-03-31",
        }

        resp = await async_client.patch("/api/equipos/vigencia", json=payload, headers=headers)

        assert resp.status_code == 200
        assert resp.json()["asignaciones_afectadas"] == 2

        asignaciones = await async_client.get(f"/api/asignaciones?materia_id={ctx['materia_id']}", headers=headers)
        data = asignaciones.json()
        for a in data:
            assert a["desde"] == "2026-04-01"
            assert a["hasta"] == "2027-03-31"

    async def test_update_solo_desde(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_vigencia_context: dict[str, Any],
    ) -> None:
        ctx = seed_vigencia_context
        headers = ctx["headers"]

        payload = {
            "materia_id": ctx["materia_id"],
            "carrera_id": ctx["carrera_id"],
            "cohorte_id": ctx["cohorte_id"],
            "desde": "2026-05-01",
        }

        resp = await async_client.patch("/api/equipos/vigencia", json=payload, headers=headers)

        assert resp.status_code == 200
        assert resp.json()["asignaciones_afectadas"] == 2

        asignaciones = await async_client.get(f"/api/asignaciones?materia_id={ctx['materia_id']}", headers=headers)
        data = asignaciones.json()
        for a in data:
            assert a["desde"] == "2026-05-01"
            assert a["hasta"] == "2026-12-31"

    async def test_update_sin_permiso_retorna_403(
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
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        payload = {
            "materia_id": "00000000-0000-0000-0000-000000000000",
            "carrera_id": "00000000-0000-0000-0000-000000000000",
            "cohorte_id": "00000000-0000-0000-0000-000000000000",
            "desde": "2026-04-01",
        }
        resp = await async_client.patch("/api/equipos/vigencia", json=payload, headers=headers)
        assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════
# 4.5 — Exportar Equipo
# ═══════════════════════════════════════════════════════════════


class TestExportarEquipo:
    """RED → GREEN: GET /api/equipos/exportar."""

    async def test_exportar_csv_contiene_cabeceras_y_filas(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_asignaciones: dict[str, Any],
    ) -> None:
        ctx = seed_asignaciones
        headers = ctx["headers"]

        resp = await async_client.get(
            f"/api/equipos/exportar?materia_id={ctx['materia_id']}&carrera_id={ctx['carrera_id']}&cohorte_id={ctx['cohorte_id']}",
            headers=headers,
        )

        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        content = resp.text

        assert content.startswith("\ufeff")
        assert "docente" in content
        assert "rol" in content
        assert "estado_vigencia" in content

    async def test_exportar_sin_parametros_retorna_422(
        self, usuarios_schema, db_session: AsyncSession, async_client: AsyncClient,
        seed_asignaciones: dict[str, Any],
    ) -> None:
        headers = await admin_headers(async_client)

        resp = await async_client.get("/api/equipos/exportar", headers=headers)

        assert resp.status_code == 422

    async def test_exportar_sin_permiso_retorna_403(
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
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        resp = await async_client.get(
            "/api/equipos/exportar?materia_id=00000000-0000-0000-0000-000000000000&carrera_id=00000000-0000-0000-0000-000000000000&cohorte_id=00000000-0000-0000-0000-000000000000",
            headers=headers,
        )
        assert resp.status_code == 403
