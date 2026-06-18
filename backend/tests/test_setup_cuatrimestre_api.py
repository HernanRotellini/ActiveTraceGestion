"""Tests para el setup de cuatrimestre: permisos y auditoria."""

from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, get_sessionmaker
from app.core.security import hash_password
from app.models.auth import AuthUser
from app.models.audit_log import AuditLog
from app.models.rbac import Permiso, Rol, RolPermiso
from app.models.tenant import Tenant


async def auth_headers(
    client: AsyncClient,
    *,
    tenant_code: str,
    email: str,
) -> dict[str, str]:
    response = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": "password"},
    )
    data = response.json()
    assert "access_token" in data, f"Login failed: {data}"
    return {"Authorization": f"Bearer {data['access_token']}"}


async def create_user_with_permissions(
    db_session: AsyncSession,
    *,
    tenant: Tenant,
    email: str,
    role_code: str,
    permissions: list[str],
) -> AuthUser:
    user = AuthUser(
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password("password"),
        roles=[role_code],
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    role = Rol(tenant_id=tenant.id, codigo=role_code, nombre=role_code)
    db_session.add(role)
    await db_session.flush()

    for permission_code in permissions:
        permiso = Permiso(
            tenant_id=tenant.id,
            codigo=permission_code,
            nombre=permission_code,
            modulo=permission_code.split(":")[0],
            accion=permission_code.split(":")[1],
        )
        db_session.add(permiso)
        await db_session.flush()
        db_session.add(
            RolPermiso(
                tenant_id=tenant.id,
                rol_id=role.id,
                permiso_id=permiso.id,
                habilitado=True,
                alcance="global",
            )
        )

    await db_session.flush()
    return user


class TestSetupCuatrimestreApi:
    async def test_periodos_endpoint_requires_estructura_permission(
        self,
        db_engine: None,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ) -> None:
        from app.services.auth import login_rate_limiter

        login_rate_limiter.reset_all()

        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            connection = await session.connection()
            await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            await connection.execute(text("CREATE SCHEMA public"))
            await connection.run_sync(Base.metadata.create_all)
            await session.commit()

        tenant = Tenant(name="Tenant setup", code="setup")
        db_session.add(tenant)
        await db_session.flush()

        await create_user_with_permissions(
            db_session,
            tenant=tenant,
            email="coord@test.com",
            role_code="COORDINADOR",
            permissions=["estructura:gestionar"],
        )
        await create_user_with_permissions(
            db_session,
            tenant=tenant,
            email="legacy@test.com",
            role_code="LEGACY",
            permissions=["periodos:gestionar"],
        )
        await db_session.commit()

        estructura_headers = await auth_headers(
            async_client, tenant_code="setup", email="coord@test.com"
        )
        legacy_headers = await auth_headers(
            async_client, tenant_code="setup", email="legacy@test.com"
        )

        ok_response = await async_client.get(
            "/api/periodos-academicos", headers=estructura_headers
        )
        forbidden_response = await async_client.get(
            "/api/periodos-academicos", headers=legacy_headers
        )

        assert ok_response.status_code == 200
        assert forbidden_response.status_code == 403

    async def test_create_and_activate_periodo_generate_audit_log(
        self,
        db_engine: None,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ) -> None:
        from app.models.permisos import PERIODO_ACTIVAR, PERIODO_CREAR
        from app.services.auth import login_rate_limiter

        login_rate_limiter.reset_all()

        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            connection = await session.connection()
            await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            await connection.execute(text("CREATE SCHEMA public"))
            await connection.run_sync(Base.metadata.create_all)
            await session.commit()

        tenant = Tenant(name="Tenant audit", code="audit-setup")
        db_session.add(tenant)
        await db_session.flush()
        await create_user_with_permissions(
            db_session,
            tenant=tenant,
            email="admin@test.com",
            role_code="ADMIN",
            permissions=["estructura:gestionar"],
        )
        await db_session.commit()

        headers = await auth_headers(
            async_client, tenant_code="audit-setup", email="admin@test.com"
        )

        create_response = await async_client.post(
            "/api/periodos-academicos",
            json={
                "nombre": "1C 2026",
                "fecha_inicio": "2026-03-01",
                "fecha_fin": "2026-07-15",
            },
            headers=headers,
        )
        assert create_response.status_code == 201
        periodo_id = create_response.json()["id"]

        activate_response = await async_client.post(
            f"/api/periodos-academicos/{periodo_id}/activar",
            headers=headers,
        )
        assert activate_response.status_code == 200

        create_audit = await db_session.execute(
            select(AuditLog).where(AuditLog.accion == PERIODO_CREAR)
        )
        activate_audit = await db_session.execute(
            select(AuditLog).where(AuditLog.accion == PERIODO_ACTIVAR)
        )

        create_entry = create_audit.scalar_one()
        activate_entry = activate_audit.scalar_one()

        assert create_entry.detalle["periodo_id"] == periodo_id
        assert create_entry.detalle["nombre"] == "1C 2026"
        assert create_entry.filas_afectadas == 1
        assert activate_entry.detalle["periodo_id"] == periodo_id
        assert activate_entry.detalle["estado_nuevo"] is True
        assert activate_entry.filas_afectadas == 1
