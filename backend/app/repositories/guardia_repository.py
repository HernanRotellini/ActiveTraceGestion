"""Repositorio tenant-scoped para guardias de atención tutorial."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardia import EstadoGuardia, Guardia
from app.repositories.base import TenantScopedRepository


class GuardiaRepository(TenantScopedRepository[Guardia]):
    """Acceso a datos de guardias, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Guardia, tenant_id)

    async def crear(self, guardia: Guardia) -> Guardia:
        self.session.add(guardia)
        await self.session.flush()
        return guardia

    async def get(self, guardia_id: UUID) -> Guardia | None:
        result = await self.session.execute(
            select(Guardia).where(
                Guardia.id == guardia_id,
                Guardia.tenant_id == self.tenant_id,
                Guardia.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def listar_con_filtros(
        self,
        materia_id: UUID | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        estado: str | None = None,
    ) -> list[Guardia]:
        stmt = (
            select(Guardia)
            .where(
                Guardia.tenant_id == self.tenant_id,
                Guardia.deleted_at.is_(None),
            )
        )
        if materia_id is not None:
            stmt = stmt.where(Guardia.materia_id == materia_id)
        if carrera_id is not None:
            stmt = stmt.where(Guardia.carrera_id == carrera_id)
        if cohorte_id is not None:
            stmt = stmt.where(Guardia.cohorte_id == cohorte_id)
        if estado is not None:
            stmt = stmt.where(Guardia.estado == estado)
        stmt = stmt.order_by(Guardia.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def actualizar_estado(
        self, guardia_id: UUID, estado: str, comentarios: str | None = None,
    ) -> Guardia | None:
        guardia = await self.get(guardia_id)
        if guardia is None:
            return None
        guardia.estado = EstadoGuardia(estado)
        if comentarios is not None:
            guardia.comentarios = comentarios
        return guardia
