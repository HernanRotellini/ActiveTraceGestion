"""Tests para C-19 Panel de Auditoría y Métricas.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.permisos import (
    AUDITORIA_VER,
    COMUNICACION_APROBAR_ACTION,
    COMUNICACION_CANCELAR,
    COMUNICACION_ENVIAR_ACTION,
)
from app.repositories.panel_auditoria import PanelAuditoriaRepository
from app.services.auth import CurrentUser
from app.services.panel_auditoria import PanelAuditoriaService


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
async def c19_schema(db_engine: None):
    from app.core.database import get_sessionmaker
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


async def create_tenant(db_session: AsyncSession, code: str = "c19-tenant") -> UUID:
    from app.models.tenant import Tenant
    tenant = Tenant(id=uuid4(), name=f"Tenant {code}", code=code)
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


async def create_auth_user(
    db_session: AsyncSession,
    tenant_id: UUID,
    *,
    email: str = "user@c19.com",
) -> UUID:
    from app.models.auth import AuthUser
    user = AuthUser(
        tenant_id=tenant_id,
        email=email,
        password_hash=hash_password("password"),
        roles=[],
    )
    db_session.add(user)
    await db_session.flush()
    return user.id


async def create_usuario(
    db_session: AsyncSession,
    tenant_id: UUID,
    *,
    nombre: str = "Docente",
    apellidos: str = "Test",
) -> UUID:
    from app.models.usuarios_asignaciones import Usuario
    usuario = Usuario(
        tenant_id=tenant_id,
        nombre=nombre,
        apellidos=apellidos,
        email=f"{nombre.lower()}@test.com",
    )
    db_session.add(usuario)
    await db_session.flush()
    return usuario.id


async def create_asignacion(
    db_session: AsyncSession,
    tenant_id: UUID,
    usuario_id: UUID,
    materia_id: UUID,
    *,
    rol: str = "COORDINADOR",
) -> UUID:
    from app.models.usuarios_asignaciones import Asignacion
    asignacion = Asignacion(
        tenant_id=tenant_id,
        usuario_id=usuario_id,
        rol=rol,
        materia_id=materia_id,
        desde=datetime.now(UTC).date(),
    )
    db_session.add(asignacion)
    await db_session.flush()
    return asignacion.id


async def create_materia(
    db_session: AsyncSession,
    tenant_id: UUID,
    *,
    codigo: str = "MAT-C19",
    nombre: str = "Materia C19",
) -> UUID:
    from app.models.estructura_academica import Materia
    materia = Materia(tenant_id=tenant_id, codigo=codigo, nombre=nombre)
    db_session.add(materia)
    await db_session.flush()
    return materia.id


async def create_audit_entry(
    db_session: AsyncSession,
    tenant_id: UUID,
    actor_id: UUID,
    *,
    accion: str = "TEST_ACTION",
    materia_id: UUID | None = None,
    fecha_hora: datetime | None = None,
) -> AuditLog:
    entry = AuditLog(
        tenant_id=tenant_id,
        actor_id=actor_id,
        accion=accion,
        materia_id=materia_id,
        detalle={},
        filas_afectadas=0,
        ip="127.0.0.1",
        user_agent="test-agent",
        fecha_hora=fecha_hora or datetime.now(UTC),
    )
    db_session.add(entry)
    await db_session.flush()
    return entry


def _make_token(user_id: UUID, tenant_id: UUID, roles: list[str]) -> str:
    from app.core.config import Settings
    settings = Settings(_env_file=None)
    return jwt.encode(
        {
            "sub": str(user_id),
            "user_id": str(user_id),
            "tenant_id": str(tenant_id),
            "roles": roles,
            "exp": datetime.now(UTC) + timedelta(hours=1),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )


# ═══════════════════════════════════════════════════════════════
# 1. Repository tests
# ═══════════════════════════════════════════════════════════════


class TestAccionesPorDia:
    async def test_acciones_dentro_de_rango(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        await db_session.commit()

        now = datetime.now(UTC)
        for i in range(3):
            await create_audit_entry(
                db_session, tenant_id, user_id, accion="ACTION",
                fecha_hora=now - timedelta(days=i),
            )
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        results = await repo.acciones_por_dia(
            fecha_desde=now - timedelta(days=5),
            fecha_hasta=now,
        )
        assert len(results) == 3

    async def test_filtro_por_materia(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        m1 = await create_materia(db_session, tenant_id, codigo="M1")
        m2 = await create_materia(db_session, tenant_id, codigo="M2")
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", materia_id=m1, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_id, accion="B", materia_id=m2, fecha_hora=now)
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        results = await repo.acciones_por_dia(materia_id=m1)
        assert len(results) == 1

    async def test_rango_vacio(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, fecha_hora=now)
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        results = await repo.acciones_por_dia(
            fecha_desde=now + timedelta(days=10),
            fecha_hasta=now + timedelta(days=20),
        )
        assert len(results) == 0

    async def test_resultados_ordenados_cronologicamente(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, fecha_hora=now - timedelta(days=2))
        await create_audit_entry(db_session, tenant_id, user_id, fecha_hora=now - timedelta(days=1))
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        results = await repo.acciones_por_dia(
            fecha_desde=now - timedelta(days=5),
            fecha_hasta=now,
        )
        assert len(results) == 2
        assert results[0]["fecha"] <= results[1]["fecha"]


class TestComunicacionesPorDocente:
    async def test_agrupadas_por_actor(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_a = await create_auth_user(db_session, tenant_id, email="a@c19.com")
        user_b = await create_auth_user(db_session, tenant_id, email="b@c19.com")
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_a, accion=COMUNICACION_ENVIAR_ACTION, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_a, accion=COMUNICACION_ENVIAR_ACTION, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_b, accion=COMUNICACION_APROBAR_ACTION, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_b, accion="OTHER_ACTION", fecha_hora=now)
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        results = await repo.comunicaciones_por_docente()
        assert len(results) == 3
        assert sum(r["total"] for r in results) == 3

    async def test_filtro_por_materia(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        m1 = await create_materia(db_session, tenant_id, codigo="M1")
        m2 = await create_materia(db_session, tenant_id, codigo="M2")
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion=COMUNICACION_ENVIAR_ACTION, materia_id=m1, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_id, accion=COMUNICACION_CANCELAR, materia_id=m2, fecha_hora=now)
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        results = await repo.comunicaciones_por_docente(materia_id=m1)
        assert len(results) == 1
        assert results[0]["accion"] == COMUNICACION_ENVIAR_ACTION


class TestInteraccionesPorDocenteMateria:
    async def test_agrupadas_por_actor_materia(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        m1 = await create_materia(db_session, tenant_id, codigo="M1")
        m2 = await create_materia(db_session, tenant_id, codigo="M2")
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", materia_id=m1, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", materia_id=m2, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_id, accion="B", materia_id=m1, fecha_hora=now)
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        results = await repo.interacciones_por_docente_materia()
        assert len(results) == 3

    async def test_filtro_por_actor(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_a = await create_auth_user(db_session, tenant_id, email="a@c19.com")
        user_b = await create_auth_user(db_session, tenant_id, email="b@c19.com")
        m1 = await create_materia(db_session, tenant_id, codigo="M1")
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_a, accion="A", materia_id=m1, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_b, accion="B", materia_id=m1, fecha_hora=now)
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        results = await repo.interacciones_por_docente_materia(actor_id=user_a)
        assert len(results) == 1
        assert results[0]["docente_id"] == user_a

    async def test_filtro_por_fecha(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        m1 = await create_materia(db_session, tenant_id, codigo="M1")
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", materia_id=m1, fecha_hora=now - timedelta(days=5))
        await create_audit_entry(db_session, tenant_id, user_id, accion="B", materia_id=m1, fecha_hora=now)
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        results = await repo.interacciones_por_docente_materia(
            fecha_desde=now - timedelta(days=1),
            fecha_hasta=now,
        )
        assert len(results) == 1
        assert results[0]["accion"] == "B"


class TestUltimasAcciones:
    async def test_default_limit(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        now = datetime.now(UTC)
        for i in range(5):
            await create_audit_entry(db_session, tenant_id, user_id, accion=f"ACT{i}", fecha_hora=now - timedelta(minutes=i))
        await db_session.commit()

        results = await repo.ultimas_acciones(limit=3)
        assert len(results) == 3

    async def test_limit_cap(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        await db_session.commit()

        repo = PanelAuditoriaRepository(db_session, tenant_id)
        now = datetime.now(UTC)
        for i in range(10):
            await create_audit_entry(db_session, tenant_id, user_id, accion=f"ACT{i}", fecha_hora=now - timedelta(minutes=i))
        await db_session.commit()

        results = await repo.ultimas_acciones(limit=1000)
        assert len(results) == 10
        assert results[0].fecha_hora >= results[-1].fecha_hora


# ═══════════════════════════════════════════════════════════════
# 2. Service scope tests
# ═══════════════════════════════════════════════════════════════


class TestPanelAuditoriaServiceScope:
    async def test_admin_ve_todo(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        m1 = await create_materia(db_session, tenant_id, codigo="M1")
        m2 = await create_materia(db_session, tenant_id, codigo="M2")
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", materia_id=m1, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_id, accion="B", materia_id=m2, fecha_hora=now)
        await db_session.commit()

        current_user = CurrentUser(user_id=user_id, tenant_id=tenant_id, roles=["ADMIN"])
        service = PanelAuditoriaService(db=db_session, current_user=current_user)
        results = await service.get_acciones_por_dia()
        assert len(results) == 2

    async def test_finanzas_ve_todo(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", fecha_hora=now)
        await db_session.commit()

        current_user = CurrentUser(user_id=user_id, tenant_id=tenant_id, roles=["FINANZAS"])
        service = PanelAuditoriaService(db=db_session, current_user=current_user)
        results = await service.get_acciones_por_dia()
        assert len(results) == 1

    async def test_coordinador_solo_sus_materias(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        m1 = await create_materia(db_session, tenant_id, codigo="M1")
        m2 = await create_materia(db_session, tenant_id, codigo="M2")
        await create_usuario(db_session, tenant_id, nombre="Coord")
        await create_asignacion(db_session, tenant_id, user_id, m1, rol="COORDINADOR")
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", materia_id=m1, fecha_hora=now)
        await create_audit_entry(db_session, tenant_id, user_id, accion="B", materia_id=m2, fecha_hora=now)
        await db_session.commit()

        current_user = CurrentUser(user_id=user_id, tenant_id=tenant_id, roles=["COORDINADOR"])
        service = PanelAuditoriaService(db=db_session, current_user=current_user)
        results = await service.get_acciones_por_dia()
        assert len(results) == 1

    async def test_coordinador_materia_fuera_de_alcance_devuelve_vacio(
        self, c19_schema: None, db_session: AsyncSession
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id)
        m1 = await create_materia(db_session, tenant_id, codigo="M1")
        m2 = await create_materia(db_session, tenant_id, codigo="M2")
        await create_asignacion(db_session, tenant_id, user_id, m1, rol="COORDINADOR")
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", materia_id=m2, fecha_hora=now)
        await db_session.commit()

        current_user = CurrentUser(user_id=user_id, tenant_id=tenant_id, roles=["COORDINADOR"])
        service = PanelAuditoriaService(db=db_session, current_user=current_user)
        results = await service.get_acciones_por_dia(materia_id=m2)
        assert len(results) == 0


# ═══════════════════════════════════════════════════════════════
# 3. API endpoint tests
# ═══════════════════════════════════════════════════════════════


class TestAuditoriaApiAuth:
    async def test_unauthenticated_gets_401(
        self, c19_schema: None, async_client: AsyncClient
    ) -> None:
        response = await async_client.get("/api/v1/auditoria/panel/acciones-por-dia")
        assert response.status_code == 401

    async def test_without_permission_gets_403(
        self, c19_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id, email="tutor@c19.com")
        await db_session.commit()

        token = _make_token(user_id, tenant_id, ["TUTOR"])
        response = await async_client.get(
            "/api/v1/auditoria/panel/acciones-por-dia",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_with_permission_gets_200(
        self, c19_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id, email="admin@c19.com")
        await db_session.commit()

        from app.models.rbac import Permiso, Rol, RolPermiso
        rol = Rol(tenant_id=tenant_id, codigo="ADMIN", nombre="Admin")
        db_session.add(rol)
        await db_session.flush()
        permiso = Permiso(
            tenant_id=tenant_id, codigo=AUDITORIA_VER, nombre="Ver auditoria",
            modulo="auditoria", accion="ver",
        )
        db_session.add(permiso)
        await db_session.flush()
        rp = RolPermiso(
            tenant_id=tenant_id, rol_id=rol.id, permiso_id=permiso.id,
            habilitado=True, alcance="global",
        )
        db_session.add(rp)
        await db_session.commit()

        token = _make_token(user_id, tenant_id, ["ADMIN"])
        response = await async_client.get(
            "/api/v1/auditoria/panel/acciones-por-dia",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


class TestAccionesPorDiaApi:
    async def test_returns_list_response(
        self, c19_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id, email="admin2@c19.com")
        await db_session.commit()

        from app.models.rbac import Permiso, Rol, RolPermiso
        rol = Rol(tenant_id=tenant_id, codigo="ADMIN", nombre="Admin")
        db_session.add(rol)
        await db_session.flush()
        permiso = Permiso(
            tenant_id=tenant_id, codigo=AUDITORIA_VER, nombre="Ver auditoria",
            modulo="auditoria", accion="ver",
        )
        db_session.add(permiso)
        await db_session.flush()
        rp = RolPermiso(
            tenant_id=tenant_id, rol_id=rol.id, permiso_id=permiso.id,
            habilitado=True, alcance="global",
        )
        db_session.add(rp)
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", fecha_hora=now)
        await db_session.commit()

        token = _make_token(user_id, tenant_id, ["ADMIN"])
        response = await async_client.get(
            "/api/v1/auditoria/panel/acciones-por-dia",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    async def test_filtro_materia_id(
        self, c19_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id, email="admin3@c19.com")
        m1 = await create_materia(db_session, tenant_id, codigo="MX")
        await db_session.commit()

        from app.models.rbac import Permiso, Rol, RolPermiso
        rol = Rol(tenant_id=tenant_id, codigo="ADMIN", nombre="Admin")
        db_session.add(rol)
        await db_session.flush()
        permiso = Permiso(
            tenant_id=tenant_id, codigo=AUDITORIA_VER, nombre="Ver auditoria",
            modulo="auditoria", accion="ver",
        )
        db_session.add(permiso)
        await db_session.flush()
        rp = RolPermiso(
            tenant_id=tenant_id, rol_id=rol.id, permiso_id=permiso.id,
            habilitado=True, alcance="global",
        )
        db_session.add(rp)
        await db_session.commit()

        now = datetime.now(UTC)
        await create_audit_entry(db_session, tenant_id, user_id, accion="A", materia_id=m1, fecha_hora=now)
        await db_session.commit()

        token = _make_token(user_id, tenant_id, ["ADMIN"])
        response = await async_client.get(
            f"/api/v1/auditoria/panel/acciones-por-dia?materia_id={m1}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


class TestUltimasAccionesApi:
    async def test_default_max_results_200(
        self, c19_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id, email="admin4@c19.com")
        await db_session.commit()

        from app.models.rbac import Permiso, Rol, RolPermiso
        rol = Rol(tenant_id=tenant_id, codigo="ADMIN", nombre="Admin")
        db_session.add(rol)
        await db_session.flush()
        permiso = Permiso(
            tenant_id=tenant_id, codigo=AUDITORIA_VER, nombre="Ver auditoria",
            modulo="auditoria", accion="ver",
        )
        db_session.add(permiso)
        await db_session.flush()
        rp = RolPermiso(
            tenant_id=tenant_id, rol_id=rol.id, permiso_id=permiso.id,
            habilitado=True, alcance="global",
        )
        db_session.add(rp)
        await db_session.commit()

        now = datetime.now(UTC)
        for i in range(5):
            await create_audit_entry(db_session, tenant_id, user_id, accion=f"ACT{i}", fecha_hora=now - timedelta(minutes=i))
        await db_session.commit()

        token = _make_token(user_id, tenant_id, ["ADMIN"])
        response = await async_client.get(
            "/api/v1/auditoria/panel/ultimas-acciones",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    async def test_custom_max_results(
        self, c19_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id, email="admin5@c19.com")
        await db_session.commit()

        from app.models.rbac import Permiso, Rol, RolPermiso
        rol = Rol(tenant_id=tenant_id, codigo="ADMIN", nombre="Admin")
        db_session.add(rol)
        await db_session.flush()
        permiso = Permiso(
            tenant_id=tenant_id, codigo=AUDITORIA_VER, nombre="Ver auditoria",
            modulo="auditoria", accion="ver",
        )
        db_session.add(permiso)
        await db_session.flush()
        rp = RolPermiso(
            tenant_id=tenant_id, rol_id=rol.id, permiso_id=permiso.id,
            habilitado=True, alcance="global",
        )
        db_session.add(rp)
        await db_session.commit()

        now = datetime.now(UTC)
        for i in range(5):
            await create_audit_entry(db_session, tenant_id, user_id, accion=f"ACT{i}", fecha_hora=now - timedelta(minutes=i))
        await db_session.commit()

        token = _make_token(user_id, tenant_id, ["ADMIN"])
        response = await async_client.get(
            "/api/v1/auditoria/panel/ultimas-acciones?max_results=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 3

    async def test_max_results_too_large_capped(
        self, c19_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant_id = await create_tenant(db_session)
        user_id = await create_auth_user(db_session, tenant_id, email="admin6@c19.com")
        await db_session.commit()

        token = _make_token(user_id, tenant_id, ["ADMIN"])
        response = await async_client.get(
            "/api/v1/auditoria/panel/ultimas-acciones?max_results=5000",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422
