"""Tests para C-04 RBAC: permisos finos, guards y administración.

Strict TDD:
  - RED:   test que falla (permiso no existe en DB)
  - GREEN: implementación mínima que pase
  - TRIANGULATE: mínimo 2 casos por comportamiento
"""

from typing import Any
from uuid import UUID

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password, hash_token
from app.models.auth import AuthUser
from app.models.rbac import Permiso, Rol, RolPermiso
from app.models.tenant import Tenant
from app.repositories.rbac import PermissionResolver, PermisoRepository, RolPermisoRepository, RolRepository


# ═══════════════════════════════════════════════════════════════
# Fixtures helpers
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
async def rbac_schema(db_engine: None):
    """Crea schema completo (tenants + auth + rbac) y lo limpia."""
    from app.core.database import get_sessionmaker
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(
            text(
                "DROP TABLE IF EXISTS roles_permisos, roles_permisos, permisos, roles, "
                "password_recovery_tokens, two_factor_challenges, "
                "totp_factors, refresh_sessions, auth_users, tenants CASCADE"
            )
        )
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


async def create_tenant(db_session: AsyncSession, code: str = "test-tenant") -> Tenant:
    tenant = Tenant(name=f"Tenant {code}", code=code)
    db_session.add(tenant)
    await db_session.flush()
    return tenant


async def create_user(
    db_session: AsyncSession,
    tenant: Tenant,
    *,
    email: str = "user@test.com",
    password: str = "password",
    roles: list[str] | None = None,
    is_active: bool = True,
) -> AuthUser:
    user = AuthUser(
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password(password),
        roles=roles or ["ALUMNO"],
        is_active=is_active,
    )
    db_session.add(user)
    await db_session.flush()
    return user


async def seed_rol(db_session: AsyncSession, tenant_id: UUID, codigo: str, nombre: str) -> Rol:
    rol = Rol(tenant_id=tenant_id, codigo=codigo, nombre=nombre)
    db_session.add(rol)
    await db_session.flush()
    return rol


async def seed_permiso(db_session: AsyncSession, tenant_id: UUID, codigo: str, modulo: str, accion: str) -> Permiso:
    p = Permiso(tenant_id=tenant_id, codigo=codigo, nombre=codigo.replace(":", " ").replace("_", " ").title(), modulo=modulo, accion=accion)
    db_session.add(p)
    await db_session.flush()
    return p


async def seed_rol_permiso(
    db_session: AsyncSession, tenant_id: UUID, rol_id: UUID, permiso_id: UUID, *, alcance: str = "global"
) -> RolPermiso:
    rp = RolPermiso(tenant_id=tenant_id, rol_id=rol_id, permiso_id=permiso_id, habilitado=True, alcance=alcance)
    db_session.add(rp)
    await db_session.flush()
    return rp


async def login(client: AsyncClient, tenant_code: str = "test-tenant", email: str = "user@test.com", password: str = "password") -> dict[str, Any]:
    response = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": password},
    )
    return response.json()


# ═══════════════════════════════════════════════════════════════
# 5.2 — 403 sin permiso
# 5.5 — 401 sin auth
# ═══════════════════════════════════════════════════════════════

class TestGuardRequirePermission:
    """RED: test que falla → GREEN: guard retorna 403 / 401."""

    async def test_authenticated_user_without_permission_gets_403(
        self, rbac_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """RED 5.2: usuario autenticado SIN permiso recibe 403."""
        tenant = await create_tenant(db_session)
        user = await create_user(db_session, tenant, roles=["ALUMNO"])
        await db_session.commit()

        payload = await login(async_client, tenant_code="test-tenant")
        token = payload["access_token"]

        response = await async_client.get(
            "/api/admin/rbac/roles",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "Forbidden" in response.json()["detail"]

    async def test_unauthenticated_request_gets_401(
        self, rbac_schema: None, async_client: AsyncClient
    ) -> None:
        """RED 5.5: sin token → 401 antes de verificar permiso."""
        response = await async_client.get("/api/admin/rbac/roles")

        assert response.status_code == 401

    async def test_missing_bearer_token_gets_401(
        self, rbac_schema: None, async_client: AsyncClient
    ) -> None:
        """TRIANGULATE: header Authorization malformado → 401."""
        response = await async_client.get(
            "/api/admin/rbac/roles",
            headers={"Authorization": "NotBearer token"},
        )

        assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════
# 5.3 — 200 con permiso
# 5.4 — Unión de roles
# 5.6 — Flag (propio)
# ═══════════════════════════════════════════════════════════════

class TestPermissionResolution:
    """RED: test que falla → GREEN: resolver permisos."""

    async def test_authenticated_user_with_permission_gets_200(
        self, rbac_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """RED 5.3: usuario ADMIN con permiso estructura:gestionar → 200."""
        tenant = await create_tenant(db_session)
        user = await create_user(db_session, tenant, roles=["ADMIN"])
        # Seed rol ADMIN + permiso + asignación
        rol = await seed_rol(db_session, tenant.id, "ADMIN", "Administrador")
        permiso = await seed_permiso(db_session, tenant.id, "estructura:gestionar", "estructura", "gestionar")
        await seed_rol_permiso(db_session, tenant.id, rol.id, permiso.id)
        await db_session.commit()

        payload = await login(async_client, tenant_code="test-tenant")
        token = payload["access_token"]

        response = await async_client.get(
            "/api/admin/rbac/roles",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_union_of_roles_produces_combined_permissions(
        self, rbac_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """RED 5.4: usuario con [TUTOR, COORDINADOR] hereda permisos de ambos."""
        tenant = await create_tenant(db_session)
        # Seed roles
        tutor = await seed_rol(db_session, tenant.id, "TUTOR", "Tutor")
        coord = await seed_rol(db_session, tenant.id, "COORDINADOR", "Coordinador")
        # Seed permisos
        p_avisos = await seed_permiso(db_session, tenant.id, "avisos:confirmar", "avisos", "confirmar")
        p_atrasados = await seed_permiso(db_session, tenant.id, "atrasados:ver", "atrasados", "ver")
        p_comunicacion = await seed_permiso(db_session, tenant.id, "comunicacion:aprobar", "comunicacion", "aprobar")
        # TUTOR gets avisos:confirmar + atrasados:ver
        await seed_rol_permiso(db_session, tenant.id, tutor.id, p_avisos.id)
        await seed_rol_permiso(db_session, tenant.id, tutor.id, p_atrasados.id)
        # COORDINADOR gets avisos:confirmar + comunicacion:aprobar
        await seed_rol_permiso(db_session, tenant.id, coord.id, p_avisos.id)
        await seed_rol_permiso(db_session, tenant.id, coord.id, p_comunicacion.id)
        user = await create_user(db_session, tenant, roles=["TUTOR", "COORDINADOR"], email="multi@test.com")
        await db_session.commit()

        resolver = PermissionResolver(db_session, tenant.id)
        efectivos = await resolver.efectivos(["TUTOR", "COORDINADOR"])

        # UNION: avisos:confirmar (shared), atrasados:ver (TUTOR), comunicacion:aprobar (COORDINADOR)
        assert "avisos:confirmar" in efectivos
        assert "atrasados:ver" in efectivos
        assert "comunicacion:aprobar" in efectivos
        assert len(efectivos) == 3

    async def test_empty_role_list_returns_empty_permissions(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: sin roles → set vacío."""
        tenant = await create_tenant(db_session)
        await db_session.commit()

        resolver = PermissionResolver(db_session, tenant.id)
        efectivos = await resolver.efectivos([])

        assert efectivos == set()

    async def test_disabled_permission_is_excluded(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        """TRIANGULATE: permiso deshabilitado no se resuelve."""
        tenant = await create_tenant(db_session)
        rol = await seed_rol(db_session, tenant.id, "TEST", "Test")
        permiso = await seed_permiso(db_session, tenant.id, "test:algo", "test", "algo")
        rp = RolPermiso(tenant_id=tenant.id, rol_id=rol.id, permiso_id=permiso.id, habilitado=False, alcance="global")
        db_session.add(rp)
        await db_session.commit()

        resolver = PermissionResolver(db_session, tenant.id)
        efectivos = await resolver.efectivos(["TEST"])

        assert "test:algo" not in efectivos


class TestPermissionAlcancePropio:
    """5.6 — Flag (propio) es informativo, no bloqueante por el guard."""

    async def test_guard_does_not_evaluate_alcance_field(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        """El guard siempre resuelve el permiso, alcance es informativo."""
        tenant = await create_tenant(db_session)
        rol = await seed_rol(db_session, tenant.id, "TUTOR", "Tutor")
        permiso = await seed_permiso(db_session, tenant.id, "guardias:registrar", "guardias", "registrar")
        await seed_rol_permiso(db_session, tenant.id, rol.id, permiso.id, alcance="propio")
        await db_session.commit()

        resolver = PermissionResolver(db_session, tenant.id)
        efectivos = await resolver.efectivos(["TUTOR"])

        # El permiso se resuelve con alcance=propio pero igual está presente
        assert "guardias:registrar" in efectivos
        # El alcance se almacena en la BD para que el endpoint lo evalúe
        result = await db_session.execute(
            text('SELECT alcance FROM roles_permisos WHERE tenant_id = :tid AND alcance = :alc'),
            {"tid": tenant.id, "alc": "propio"},
        )
        assert result.scalar_one() == "propio"


# ═══════════════════════════════════════════════════════════════
# 5.7 — Admin catalog CRUD
# ═══════════════════════════════════════════════════════════════

class TestAdminRbacCatalog:
    """5.7 — El catálogo es administrable (crear rol, asignar permiso, verificar)."""

    async def test_catalog_create_role_and_assign_permission(
        self, rbac_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """Crear nuevo rol, asignarle permiso, verificar que se resuelve."""
        tenant = await create_tenant(db_session)
        # Seed ADMIN with estructura:gestionar for API access
        admin_rol = await seed_rol(db_session, tenant.id, "ADMIN", "Administrador")
        admin_perm = await seed_permiso(db_session, tenant.id, "estructura:gestionar", "estructura", "gestionar")
        await seed_rol_permiso(db_session, tenant.id, admin_rol.id, admin_perm.id)
        user = await create_user(db_session, tenant, roles=["ADMIN"])
        await db_session.commit()

        payload = await login(async_client, tenant_code="test-tenant")
        token = payload["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create new rol via API
        create_resp = await async_client.post(
            "/api/admin/rbac/roles",
            params={"codigo": "SUPERVISOR", "nombre": "Supervisor"},
            headers=headers,
        )
        assert create_resp.status_code == 201
        new_rol = create_resp.json()
        assert new_rol["codigo"] == "SUPERVISOR"

        # List roles
        list_resp = await async_client.get("/api/admin/rbac/roles", headers=headers)
        assert list_resp.status_code == 200
        codigos = [r["codigo"] for r in list_resp.json()]
        assert "SUPERVISOR" in codigos

    async def test_catalog_create_duplicate_role_returns_409(
        self, rbac_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """Crear rol duplicado → 409 Conflict."""
        tenant = await create_tenant(db_session)
        admin_rol = await seed_rol(db_session, tenant.id, "ADMIN", "Administrador")
        admin_perm = await seed_permiso(db_session, tenant.id, "estructura:gestionar", "estructura", "gestionar")
        await seed_rol_permiso(db_session, tenant.id, admin_rol.id, admin_perm.id)
        user = await create_user(db_session, tenant, roles=["ADMIN"])
        await db_session.commit()

        payload = await login(async_client, tenant_code="test-tenant")
        token = payload["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        await async_client.post(
            "/api/admin/rbac/roles",
            params={"codigo": "SUPERVISOR", "nombre": "Supervisor"},
            headers=headers,
        )
        dup = await async_client.post(
            "/api/admin/rbac/roles",
            params={"codigo": "SUPERVISOR", "nombre": "Otro"},
            headers=headers,
        )

        assert dup.status_code == 409


# ═══════════════════════════════════════════════════════════════
# Repository-level tests
# ═══════════════════════════════════════════════════════════════

class TestRolRepository:
    """Tests directos de RolRepository."""

    async def test_create_and_get_by_code(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        await db_session.commit()
        repo = RolRepository(db_session, tenant.id)

        rol = await repo.create(codigo="TEST", nombre="Test Role")
        found = await repo.get_by_code("TEST")

        assert found is not None
        assert found.id == rol.id
        assert found.codigo == "TEST"
        assert found.nombre == "Test Role"

    async def test_get_by_code_does_not_cross_tenants(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        t1 = await create_tenant(db_session, "t1")
        t2 = await create_tenant(db_session, "t2")
        await db_session.commit()
        repo1 = RolRepository(db_session, t1.id)
        repo2 = RolRepository(db_session, t2.id)

        await repo1.create(codigo="X", nombre="X")
        found = await repo2.get_by_code("X")

        assert found is None

    async def test_soft_delete_hides_role(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        await db_session.commit()
        repo = RolRepository(db_session, tenant.id)

        rol = await repo.create(codigo="DEL", nombre="Delete Me")
        await repo.soft_delete(rol.id)

        found = await repo.get_by_code("DEL")
        assert found is None


class TestPermisoRepository:
    """Tests directos de PermisoRepository."""

    async def test_create_and_get_by_code(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        await db_session.commit()
        repo = PermisoRepository(db_session, tenant.id)

        p = await repo.create(codigo="mod:acc", nombre="Mod Accion", modulo="mod", accion="acc")
        found = await repo.get_by_code("mod:acc")

        assert found is not None
        assert found.id == p.id
        assert found.codigo == "mod:acc"
        assert found.modulo == "mod"
        assert found.accion == "acc"


class TestRolPermisoRepository:
    """Tests directos de RolPermisoRepository."""

    async def test_get_permisos_efectivos_multiple_roles(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        await db_session.commit()
        repo_rol = RolRepository(db_session, tenant.id)
        repo_perm = PermisoRepository(db_session, tenant.id)
        repo_rp = RolPermisoRepository(db_session, tenant.id)

        a = await repo_rol.create(codigo="A", nombre="A")
        b = await repo_rol.create(codigo="B", nombre="B")
        p1 = await repo_perm.create(codigo="x:1", nombre="X1", modulo="x", accion="1")
        p2 = await repo_perm.create(codigo="x:2", nombre="X2", modulo="x", accion="2")
        p3 = await repo_perm.create(codigo="x:3", nombre="X3", modulo="x", accion="3")

        await repo_rp.assign(a.id, p1.id)
        await repo_rp.assign(a.id, p2.id)
        await repo_rp.assign(b.id, p2.id)
        await repo_rp.assign(b.id, p3.id)

        efectivos = await repo_rp.get_permisos_efectivos(["A", "B"])

        assert efectivos == {"x:1", "x:2", "x:3"}

    async def test_empty_roles_returns_empty(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        await db_session.commit()
        repo_rp = RolPermisoRepository(db_session, tenant.id)
        efectivos = await repo_rp.get_permisos_efectivos([])
        assert efectivos == set()

    async def test_assign_and_remove(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        await db_session.commit()
        repo_rol = RolRepository(db_session, tenant.id)
        repo_perm = PermisoRepository(db_session, tenant.id)
        repo_rp = RolPermisoRepository(db_session, tenant.id)

        rol = await repo_rol.create(codigo="R", nombre="R")
        perm = await repo_perm.create(codigo="m:a", nombre="M A", modulo="m", accion="a")
        rp = await repo_rp.assign(rol.id, perm.id)

        assert rp.habilitado is True
        assert rp.alcance == "global"

        removed = await repo_rp.remove(rol.id, perm.id)
        assert removed is True

        efectivos = await repo_rp.get_permisos_efectivos(["R"])
        assert efectivos == set()


class TestPermissionResolver:
    """Tests de PermissionResolver como servicio."""

    async def test_resolver_delegates_to_repo(
        self, rbac_schema: None, db_session: AsyncSession
    ) -> None:
        tenant = await create_tenant(db_session)
        await db_session.commit()
        repo_rol = RolRepository(db_session, tenant.id)
        repo_perm = PermisoRepository(db_session, tenant.id)
        repo_rp = RolPermisoRepository(db_session, tenant.id)

        rol = await repo_rol.create(codigo="X", nombre="X")
        perm = await repo_perm.create(codigo="test:permiso", nombre="Test", modulo="test", accion="permiso")
        await repo_rp.assign(rol.id, perm.id)

        resolver = PermissionResolver(db_session, tenant.id)
        efectivos = await resolver.efectivos(["X"])

        assert "test:permiso" in efectivos
