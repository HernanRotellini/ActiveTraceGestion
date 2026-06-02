"""Repositories tenant-scoped para RBAC."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rbac import Permiso, Rol, RolPermiso
from app.repositories.base import TenantScopedRepository


class RolRepository(TenantScopedRepository[Rol]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Rol, tenant_id)

    async def get_by_code(self, codigo: str) -> Rol | None:
        result = await self.session.execute(
            select(Rol).where(
                Rol.tenant_id == self.tenant_id,
                Rol.deleted_at.is_(None),
                Rol.codigo == codigo,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, codigo: str, nombre: str) -> Rol:
        record = Rol(tenant_id=self.tenant_id, codigo=codigo, nombre=nombre)
        self.session.add(record)
        await self.session.flush()
        return record

    async def update(self, rol_id: UUID, *, codigo: str | None = None, nombre: str | None = None) -> Rol | None:
        record = await self.get(rol_id)
        if record is None:
            return None
        if codigo is not None:
            record.codigo = codigo
        if nombre is not None:
            record.nombre = nombre
        return record


class PermisoRepository(TenantScopedRepository[Permiso]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Permiso, tenant_id)

    async def get_by_code(self, codigo: str) -> Permiso | None:
        result = await self.session.execute(
            select(Permiso).where(
                Permiso.tenant_id == self.tenant_id,
                Permiso.deleted_at.is_(None),
                Permiso.codigo == codigo,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, codigo: str, nombre: str, modulo: str, accion: str) -> Permiso:
        record = Permiso(tenant_id=self.tenant_id, codigo=codigo, nombre=nombre, modulo=modulo, accion=accion)
        self.session.add(record)
        await self.session.flush()
        return record


class RolPermisoRepository(TenantScopedRepository[RolPermiso]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, RolPermiso, tenant_id)

    async def get_permisos_efectivos(self, role_codes: list[str]) -> set[str]:
        if not role_codes:
            return set()
        result = await self.session.execute(
            select(Permiso.codigo)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .join(Rol, RolPermiso.rol_id == Rol.id)
            .where(
                Rol.codigo.in_(role_codes),
                Rol.tenant_id == self.tenant_id,
                Rol.deleted_at.is_(None),
                Permiso.tenant_id == self.tenant_id,
                Permiso.deleted_at.is_(None),
                RolPermiso.tenant_id == self.tenant_id,
                RolPermiso.deleted_at.is_(None),
                RolPermiso.habilitado.is_(True),
            )
        )
        return set(result.scalars().all())

    async def assign(self, rol_id: UUID, permiso_id: UUID, *, habilitado: bool = True, alcance: str = "global") -> RolPermiso:
        record = RolPermiso(
            tenant_id=self.tenant_id,
            rol_id=rol_id,
            permiso_id=permiso_id,
            habilitado=habilitado,
            alcance=alcance,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def remove(self, rol_id: UUID, permiso_id: UUID) -> bool:
        result = await self.session.execute(
            select(RolPermiso).where(
                RolPermiso.tenant_id == self.tenant_id,
                RolPermiso.rol_id == rol_id,
                RolPermiso.permiso_id == permiso_id,
                RolPermiso.deleted_at.is_(None),
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            return False
        await self.soft_delete(record.id)
        return True


class PermissionResolver:
    """Resolver stateless de permisos efectivos para un set de roles."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._repo = RolPermisoRepository(session, tenant_id)

    async def efectivos(self, role_codes: list[str]) -> set[str]:
        if not role_codes:
            return set()
        return await self._repo.get_permisos_efectivos(role_codes)
