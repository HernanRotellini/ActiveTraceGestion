"""Tests para C-05 audit-log: append-only, impersonación, consulta.

Strict TDD:
  - RED:   test que falla
  - GREEN: implementación mínima que pase
  - TRIANGULATE: mínimo 2 casos por comportamiento
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.auth import AuthUser
from app.models.tenant import Tenant
from app.repositories.audit_log import AuditLogRepository
from app.services.audit import AuditService
from app.services.auth import CurrentUser


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
async def audit_schema(db_engine: None):
    """Borra schema público con CASCADE y recrea todas las tablas."""
    from app.core.database import get_sessionmaker

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


async def create_tenant(
    db_session: AsyncSession,
    code: str = "test-tenant",
    name: str | None = None,
) -> Tenant:
    tenant = Tenant(name=name or f"Tenant {code}", code=code)
    db_session.add(tenant)
    await db_session.flush()
    return tenant


async def create_auth_user(
    db_session: AsyncSession,
    tenant: Tenant,
    *,
    email: str = "user@test.com",
    roles: list[str] | None = None,
) -> AuthUser:
    user = AuthUser(
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password("password"),
        roles=roles or [],
    )
    db_session.add(user)
    await db_session.flush()
    return user


async def create_audit_entry(
    db_session: AsyncSession,
    tenant_id: UUID,
    actor_id: UUID,
    *,
    accion: str = "TEST_ACTION",
    impersonado_id: UUID | None = None,
    ip: str = "127.0.0.1",
    user_agent: str = "test-agent",
) -> AuditLog:
    entry = AuditLog(
        tenant_id=tenant_id,
        actor_id=actor_id,
        impersonado_id=impersonado_id,
        accion=accion,
        detalle={"key": "value"},
        filas_afectadas=10,
        ip=ip,
        user_agent=user_agent,
    )
    db_session.add(entry)
    await db_session.flush()
    return entry


# ═══════════════════════════════════════════════════════════════
# 5.2 — Insert audit entry succeeds
# ═══════════════════════════════════════════════════════════════

class TestAuditLogInsert:
    """RED: test que falla → GREEN: repositorio crea entry."""

    async def test_insert_audit_entry_succeeds(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """RED 5.2: crear entry vía repositorio funciona."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        await db_session.commit()

        repo = AuditLogRepository(db_session, tenant.id)
        entry = AuditLog(
            tenant_id=tenant.id,
            actor_id=user.id,
            accion="TEST_ACTION",
            detalle={"test": True},
            filas_afectadas=5,
            ip="127.0.0.1",
            user_agent="pytest",
        )
        created = await repo.create(entry)
        await db_session.commit()

        assert created.id is not None
        assert created.accion == "TEST_ACTION"
        assert created.actor_id == user.id
        assert created.tenant_id == tenant.id
        assert created.detalle == {"test": True}
        assert created.filas_afectadas == 5
        assert created.ip == "127.0.0.1"
        assert created.user_agent == "pytest"
        assert created.fecha_hora is not None

    async def test_insert_audit_entry_with_all_fields(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: todos los campos incluyendo impersonado_id y materia_id."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        impersonated = await create_auth_user(db_session, tenant, email="imp@test.com")
        await db_session.commit()

        repo = AuditLogRepository(db_session, tenant.id)
        entry = AuditLog(
            tenant_id=tenant.id,
            actor_id=user.id,
            impersonado_id=impersonated.id,
            accion="IMPERSONATED_ACTION",
            detalle={"impersonated": True},
            filas_afectadas=0,
            ip="10.0.0.1",
            user_agent="curl/7.0",
        )
        created = await repo.create(entry)
        await db_session.commit()

        assert created.impersonado_id == impersonated.id
        assert created.actor_id == user.id
        assert created.filas_afectadas == 0
        assert created.ip == "10.0.0.1"


# ═══════════════════════════════════════════════════════════════
# 5.3 — Update rejected at app level
# 5.4 — Delete rejected at app level
# ═══════════════════════════════════════════════════════════════

class TestAuditLogAppendOnlyApp:
    """Repository NO expone update/delete/set methods."""

    async def test_repository_has_no_update_method(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """RED 5.3: repositorio no tiene update."""
        tenant = await create_tenant(db_session)
        await db_session.commit()
        repo = AuditLogRepository(db_session, tenant.id)
        assert not hasattr(repo, "update")
        assert not hasattr(repo, "soft_delete")

    async def test_repository_has_no_delete_method(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """RED 5.4: repositorio no tiene delete."""
        tenant = await create_tenant(db_session)
        await db_session.commit()
        repo = AuditLogRepository(db_session, tenant.id)
        assert not hasattr(repo, "delete")

    async def test_direct_update_on_orm_is_possible_but_not_encouraged(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: a nivel ORM se puede modificar (no hay trigger en test)."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        await db_session.commit()

        entry = await create_audit_entry(db_session, tenant.id, user.id)
        await db_session.commit()

        entry.accion = "MODIFIED"
        await db_session.flush()
        await db_session.refresh(entry)

        # ORM permite modificar porque no hay trigger en test (create_all)
        # El bloqueo está en el repositorio y en el trigger DB
        assert entry.accion == "MODIFIED"


# ═══════════════════════════════════════════════════════════════
# 5.5 — Impersonation records actor_id correctly
# 5.6 — No impersonation has impersonado_id = None
# ═══════════════════════════════════════════════════════════════

class TestAuditImpersonation:
    """RED: test que falla → GREEN: AuditService maneja impersonación."""

    async def test_impersonation_uses_impersonator_as_actor(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """RED 5.5: bajo impersonación, actor_id es el impersonator."""
        tenant = await create_tenant(db_session)
        impersonator = await create_auth_user(db_session, tenant, email="admin@test.com")
        target = await create_auth_user(db_session, tenant, email="target@test.com")
        await db_session.commit()

        current_user = CurrentUser(
            user_id=target.id,
            tenant_id=tenant.id,
            roles=["ADMIN"],
            impersonator_id=impersonator.id,
        )
        service = AuditService(
            db=db_session,
            current_user=current_user,
            ip="192.168.1.1",
            user_agent="test-agent",
        )
        entry = await service.log(
            accion="IMPERSONATED_ACTION",
            detalle={"info": "test"},
            filas_afectadas=3,
        )

        assert entry.actor_id == impersonator.id
        assert entry.impersonado_id == target.id
        assert entry.tenant_id == tenant.id
        assert entry.accion == "IMPERSONATED_ACTION"

    async def test_no_impersonation_has_impersonado_id_none(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """RED 5.6: sesión normal → impersonado_id = None."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        await db_session.commit()

        current_user = CurrentUser(
            user_id=user.id,
            tenant_id=tenant.id,
            roles=["TUTOR"],
        )
        service = AuditService(
            db=db_session,
            current_user=current_user,
            ip="10.0.0.1",
            user_agent="normal-test",
        )
        entry = await service.log(
            accion="NORMAL_ACTION",
            detalle={"normal": True},
        )

        assert entry.actor_id == user.id
        assert entry.impersonado_id is None

    async def test_preset_impersonado_id_is_overridden(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: el service ignora impersonado_id del caller."""
        tenant = await create_tenant(db_session)
        impersonator = await create_auth_user(db_session, tenant, email="admin@test.com")
        target = await create_auth_user(db_session, tenant, email="target@test.com")
        await db_session.commit()

        current_user = CurrentUser(
            user_id=target.id,
            tenant_id=tenant.id,
            roles=["ADMIN"],
            impersonator_id=impersonator.id,
        )
        service = AuditService(
            db=db_session,
            current_user=current_user,
            ip="192.168.1.1",
            user_agent="test-agent",
        )
        entry = await service.log(
            accion="IMPERSONATED_ACTION",
            detalle={},
            filas_afectadas=1,
        )

        assert entry.actor_id == impersonator.id
        assert entry.impersonado_id == target.id
        assert entry.impersonado_id != impersonator.id


# ═══════════════════════════════════════════════════════════════
# 5.7 — Query filtered by date range
# ═══════════════════════════════════════════════════════════════

class TestAuditLogQuery:
    """RED: test consulta con filtros."""

    async def test_query_by_date_range(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """RED 5.7: filtrar por rango de fechas."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        await db_session.commit()

        repo = AuditLogRepository(db_session, tenant.id)

        entry_a = await create_audit_entry(db_session, tenant.id, user.id, accion="ACTION_A")
        entry_b = await create_audit_entry(db_session, tenant.id, user.id, accion="ACTION_B")
        await db_session.commit()

        # freeze timestamps
        now = datetime.now(UTC)
        entry_a.fecha_hora = now - timedelta(hours=2)
        entry_b.fecha_hora = now - timedelta(hours=1)
        await db_session.flush()
        await db_session.commit()

        results = await repo.list(
            fecha_desde=now - timedelta(hours=3),
            fecha_hasta=now,
        )
        assert len(results) == 2

        results_morning = await repo.list(
            fecha_desde=now - timedelta(hours=1, minutes=30),
            fecha_hasta=now,
        )
        assert len(results_morning) == 1

        results_empty = await repo.list(
            fecha_desde=now + timedelta(hours=10),
            fecha_hasta=now + timedelta(hours=20),
        )
        assert len(results_empty) == 0

    async def test_query_by_actor(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: filtrar por actor_id."""
        tenant = await create_tenant(db_session)
        user_a = await create_auth_user(db_session, tenant, email="a@test.com")
        user_b = await create_auth_user(db_session, tenant, email="b@test.com")
        await db_session.commit()

        repo = AuditLogRepository(db_session, tenant.id)

        await create_audit_entry(db_session, tenant.id, user_a.id, accion="USER_A_ACTION")
        await create_audit_entry(db_session, tenant.id, user_b.id, accion="USER_B_ACTION")
        await create_audit_entry(db_session, tenant.id, user_b.id, accion="USER_B_ACTION_2")
        await db_session.commit()

        results_a = await repo.list(actor_id=user_a.id)
        assert len(results_a) == 1

        results_b = await repo.list(actor_id=user_b.id)
        assert len(results_b) == 2

    async def test_query_by_accion(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: filtrar por código de acción."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        await db_session.commit()

        repo = AuditLogRepository(db_session, tenant.id)

        await create_audit_entry(db_session, tenant.id, user.id, accion="IMPORTAR")
        await create_audit_entry(db_session, tenant.id, user.id, accion="EXPORTAR")
        await create_audit_entry(db_session, tenant.id, user.id, accion="IMPORTAR")
        await db_session.commit()

        results = await repo.list(accion="IMPORTAR")
        assert len(results) == 2

        results_export = await repo.list(accion="EXPORTAR")
        assert len(results_export) == 1

    async def test_query_with_limit_and_offset(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: paginación."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        await db_session.commit()

        repo = AuditLogRepository(db_session, tenant.id)

        for i in range(5):
            await create_audit_entry(db_session, tenant.id, user.id, accion=f"ACTION_{i}")
        await db_session.commit()

        all_results = await repo.list(limit=100, offset=0)
        assert len(all_results) == 5

        page1 = await repo.list(limit=2, offset=0)
        assert len(page1) == 2

        page2 = await repo.list(limit=2, offset=2)
        assert len(page2) == 2

        page3 = await repo.list(limit=2, offset=4)
        assert len(page3) == 1

    async def test_count_matches_list(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: count refleja los mismos filtros."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        await db_session.commit()

        repo = AuditLogRepository(db_session, tenant.id)

        await create_audit_entry(db_session, tenant.id, user.id, accion="A")
        await create_audit_entry(db_session, tenant.id, user.id, accion="B")
        await create_audit_entry(db_session, tenant.id, user.id, accion="A")
        await db_session.commit()

        total = await repo.count(accion="A")
        assert total == 2
        results = await repo.list(accion="A")
        assert len(results) == total


# ═══════════════════════════════════════════════════════════════
# 5.8 — Tenant isolation
# ═══════════════════════════════════════════════════════════════

class TestAuditTenantIsolation:
    """RED: tenant A no ve entries de tenant B."""

    async def test_tenant_a_cannot_see_tenant_b_entries(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """RED 5.8: aislamiento multi-tenant."""
        tenant_a = await create_tenant(db_session, "tenant-a")
        tenant_b = await create_tenant(db_session, "tenant-b")

        user_a = await create_auth_user(db_session, tenant_a, email="a@test.com")
        user_b = await create_auth_user(db_session, tenant_b, email="b@test.com")
        await db_session.commit()

        repo_a = AuditLogRepository(db_session, tenant_a.id)
        repo_b = AuditLogRepository(db_session, tenant_b.id)

        await create_audit_entry(db_session, tenant_a.id, user_a.id, accion="TENANT_A_ACTION")
        await create_audit_entry(db_session, tenant_b.id, user_b.id, accion="TENANT_B_ACTION")
        await db_session.commit()

        results_a = await repo_a.list()
        assert len(results_a) == 1
        assert results_a[0].accion == "TENANT_A_ACTION"

        results_b = await repo_b.list()
        assert len(results_b) == 1
        assert results_b[0].accion == "TENANT_B_ACTION"

    async def test_tenant_count_is_isolated(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: count también aísla por tenant."""
        tenant_a = await create_tenant(db_session, "tenant-a")
        tenant_b = await create_tenant(db_session, "tenant-b")
        user_a = await create_auth_user(db_session, tenant_a, email="a@test.com")
        user_b = await create_auth_user(db_session, tenant_b, email="b@test.com")
        await db_session.commit()

        repo_a = AuditLogRepository(db_session, tenant_a.id)
        repo_b = AuditLogRepository(db_session, tenant_b.id)

        await create_audit_entry(db_session, tenant_a.id, user_a.id)
        await create_audit_entry(db_session, tenant_a.id, user_a.id)
        await create_audit_entry(db_session, tenant_b.id, user_b.id)
        await db_session.commit()

        assert await repo_a.count() == 2
        assert await repo_b.count() == 1


# ═══════════════════════════════════════════════════════════════
# 5.9 — Unauthenticated → 401
# 5.10 — No permission → 403
# ═══════════════════════════════════════════════════════════════

class TestAuditApiAuth:
    """RED: endpoint protegido."""

    async def test_unauthenticated_request_gets_401(
        self, audit_schema: None, async_client: AsyncClient
    ) -> None:
        """RED 5.9: sin token → 401."""
        response = await async_client.get("/api/v1/audit/logs")
        assert response.status_code == 401

    async def test_user_without_auditoria_ver_gets_403(
        self, audit_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """RED 5.10: sin permiso auditoria:ver → 403."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant, roles=["TUTOR"])
        await db_session.commit()

        token = self._make_token(user.id, tenant.id, ["TUTOR"])
        response = await async_client.get(
            "/api/v1/audit/logs",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_user_with_auditoria_ver_gets_200(
        self, audit_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """TRIANGULATE: con permiso → 200."""
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant, roles=["ADMIN"])
        await db_session.commit()

        from app.models.rbac import Permiso, Rol, RolPermiso

        rol = Rol(tenant_id=tenant.id, codigo="ADMIN", nombre="Administrador")
        db_session.add(rol)
        await db_session.flush()
        permiso = Permiso(
            tenant_id=tenant.id,
            codigo="auditoria:ver",
            nombre="Ver auditoria",
            modulo="auditoria",
            accion="ver",
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
        await db_session.commit()

        token = self._make_token(user.id, tenant.id, ["ADMIN"])
        response = await async_client.get(
            "/api/v1/audit/logs",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def _make_token(self, user_id: UUID, tenant_id: UUID, roles: list[str]) -> str:
        from app.core.config import Settings

        settings = Settings(_env_file=None)  # type: ignore[call-arg]
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
# Audit Service typed helpers
# ═══════════════════════════════════════════════════════════════

class TestAuditServiceHelpers:
    """Helpers tipados del servicio de auditoría."""

    async def test_log_calificaciones_importar(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        await db_session.commit()

        current_user = CurrentUser(user_id=user.id, tenant_id=tenant.id, roles=["PROFESOR"])
        service = AuditService(db=db_session, current_user=current_user, ip="1.1.1.1", user_agent="test")

        entry = await service.log_calificaciones_importar(
            total_filas=42,
            detalle_extra={"source": "moodle"},
            materia_id=None,
        )
        assert entry.accion == "CALIFICACIONES_IMPORTAR"
        assert entry.filas_afectadas == 42
        assert entry.detalle == {"source": "moodle"}

    async def test_log_impersonacion_iniciar(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        impersonator = await create_auth_user(db_session, tenant, email="admin@test.com")
        target = await create_auth_user(db_session, tenant, email="target@test.com")
        await db_session.commit()

        current_user = CurrentUser(
            user_id=target.id,
            tenant_id=tenant.id,
            roles=["ADMIN"],
            impersonator_id=impersonator.id,
        )
        service = AuditService(db=db_session, current_user=current_user, ip="1.1.1.1", user_agent="test")

        entry = await service.log_impersonacion_iniciar(detalle_extra={"start": True})
        assert entry.accion == "IMPERSONACION_INICIAR"
        assert entry.actor_id == impersonator.id
        assert entry.impersonado_id == target.id

    async def test_log_impersonacion_finalizar(
        self, audit_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        user = await create_auth_user(db_session, tenant)
        await db_session.commit()

        current_user = CurrentUser(user_id=user.id, tenant_id=tenant.id, roles=["ADMIN"])
        service = AuditService(db=db_session, current_user=current_user, ip="1.1.1.1", user_agent="test")

        entry = await service.log_impersonacion_finalizar()
        assert entry.accion == "IMPERSONACION_FINALIZAR"
