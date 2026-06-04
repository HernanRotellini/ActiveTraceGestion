"""Repositorio tenant-scoped para slots e instancias de encuentro."""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.encuentro import InstanciaEncuentro, SlotEncuentro
from app.repositories.base import TenantScopedRepository


class EncuentroRepository(TenantScopedRepository[SlotEncuentro]):
    """Acceso a datos de slots e instancias de encuentro, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, SlotEncuentro, tenant_id)

    # ── SlotEncuentro ───────────────────────────────────────────

    async def crear_slot(self, slot: SlotEncuentro) -> SlotEncuentro:
        self.session.add(slot)
        await self.session.flush()
        return slot

    async def get_slot(self, slot_id: UUID) -> SlotEncuentro | None:
        return await self.get(slot_id)

    async def listar_slots(
        self, materia_id: UUID | None = None,
    ) -> list[SlotEncuentro]:
        stmt = (
            select(SlotEncuentro)
            .where(
                SlotEncuentro.tenant_id == self.tenant_id,
                SlotEncuentro.deleted_at.is_(None),
            )
        )
        if materia_id is not None:
            stmt = stmt.where(SlotEncuentro.materia_id == materia_id)
        stmt = stmt.order_by(SlotEncuentro.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ── InstanciaEncuentro ──────────────────────────────────────

    async def crear_instancias_bulk(
        self, instancias: list[InstanciaEncuentro],
    ) -> list[InstanciaEncuentro]:
        self.session.add_all(instancias)
        await self.session.flush()
        return instancias

    async def get_instancia(self, instancia_id: UUID) -> InstanciaEncuentro | None:
        result = await self.session.execute(
            select(InstanciaEncuentro).where(
                InstanciaEncuentro.id == instancia_id,
                InstanciaEncuentro.tenant_id == self.tenant_id,
                InstanciaEncuentro.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def listar_instancias(
        self, materia_id: UUID | None = None,
    ) -> list[InstanciaEncuentro]:
        stmt = (
            select(InstanciaEncuentro)
            .where(
                InstanciaEncuentro.tenant_id == self.tenant_id,
                InstanciaEncuentro.deleted_at.is_(None),
            )
        )
        if materia_id is not None:
            stmt = stmt.where(InstanciaEncuentro.materia_id == materia_id)
        stmt = stmt.order_by(InstanciaEncuentro.fecha, InstanciaEncuentro.hora)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def actualizar_instancia(
        self, instancia_id: UUID, **kwargs,
    ) -> InstanciaEncuentro | None:
        instancia = await self.get_instancia(instancia_id)
        if instancia is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(instancia, key, value)
        return instancia

    async def listar_admin(
        self,
        materia_id: UUID | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        estado: str | None = None,
    ) -> list[InstanciaEncuentro]:
        stmt = (
            select(InstanciaEncuentro)
            .where(
                InstanciaEncuentro.tenant_id == self.tenant_id,
                InstanciaEncuentro.deleted_at.is_(None),
            )
        )
        if materia_id is not None:
            stmt = stmt.where(InstanciaEncuentro.materia_id == materia_id)
        if fecha_desde is not None:
            stmt = stmt.where(InstanciaEncuentro.fecha >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(InstanciaEncuentro.fecha <= fecha_hasta)
        if estado is not None:
            stmt = stmt.where(InstanciaEncuentro.estado == estado)
        stmt = stmt.order_by(InstanciaEncuentro.fecha, InstanciaEncuentro.hora)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
