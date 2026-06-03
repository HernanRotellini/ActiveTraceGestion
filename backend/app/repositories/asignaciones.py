"""Repository tenant-scoped para Asignacion."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usuarios_asignaciones import Asignacion
from app.repositories.base import TenantScopedRepository


class AsignacionRepository(TenantScopedRepository[Asignacion]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Asignacion, tenant_id)

    async def list_by_materia(self, materia_id: UUID) -> list[Asignacion]:
        result = await self.session.execute(
            select(Asignacion).where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.materia_id == materia_id,
            )
        )
        return list(result.scalars().all())

    async def list_by_usuario(self, usuario_id: UUID) -> list[Asignacion]:
        result = await self.session.execute(
            select(Asignacion).where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.usuario_id == usuario_id,
            )
        )
        return list(result.scalars().all())

    async def list_by_rol(self, rol: str) -> list[Asignacion]:
        result = await self.session.execute(
            select(Asignacion).where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.rol == rol,
            )
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Asignacion:
        record = Asignacion(tenant_id=self.tenant_id, **kwargs)
        self.session.add(record)
        await self.session.flush()
        return record

    async def update(self, asignacion_id: UUID, **kwargs) -> Asignacion | None:
        record = await self.get(asignacion_id)
        if record is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(record, key, value)
        await self.session.flush()
        return record
