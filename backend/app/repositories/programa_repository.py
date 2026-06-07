"""Repositorio tenant-scoped para programas de materia."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.programas import ProgramaMateria
from app.repositories.base import TenantScopedRepository


class ProgramaMateriaRepository(TenantScopedRepository[ProgramaMateria]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, ProgramaMateria, tenant_id)

    async def create(
        self, *, materia_id: UUID, carrera_id: UUID, cohorte_id: UUID, titulo: str, referencia_archivo: str
    ) -> ProgramaMateria:
        programa = ProgramaMateria(
            tenant_id=self.tenant_id,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            titulo=titulo,
            referencia_archivo=referencia_archivo,
        )
        self.session.add(programa)
        await self.session.flush()
        return programa

    async def list_by_materia(self, materia_id: UUID) -> list[ProgramaMateria]:
        result = await self.session.execute(
            select(ProgramaMateria).where(
                ProgramaMateria.tenant_id == self.tenant_id,
                ProgramaMateria.deleted_at.is_(None),
                ProgramaMateria.materia_id == materia_id,
            )
        )
        return list(result.scalars().all())

    async def list_by_carrera(self, carrera_id: UUID) -> list[ProgramaMateria]:
        result = await self.session.execute(
            select(ProgramaMateria).where(
                ProgramaMateria.tenant_id == self.tenant_id,
                ProgramaMateria.deleted_at.is_(None),
                ProgramaMateria.carrera_id == carrera_id,
            )
        )
        return list(result.scalars().all())

    async def list_by_cohorte(self, cohorte_id: UUID) -> list[ProgramaMateria]:
        result = await self.session.execute(
            select(ProgramaMateria).where(
                ProgramaMateria.tenant_id == self.tenant_id,
                ProgramaMateria.deleted_at.is_(None),
                ProgramaMateria.cohorte_id == cohorte_id,
            )
        )
        return list(result.scalars().all())

    async def list_filtered(
        self, *, materia_id: UUID | None = None, carrera_id: UUID | None = None, cohorte_id: UUID | None = None
    ) -> list[ProgramaMateria]:
        where = [
            ProgramaMateria.tenant_id == self.tenant_id,
            ProgramaMateria.deleted_at.is_(None),
        ]
        if materia_id is not None:
            where.append(ProgramaMateria.materia_id == materia_id)
        if carrera_id is not None:
            where.append(ProgramaMateria.carrera_id == carrera_id)
        if cohorte_id is not None:
            where.append(ProgramaMateria.cohorte_id == cohorte_id)
        result = await self.session.execute(select(ProgramaMateria).where(*where))
        return list(result.scalars().all())

    async def update(
        self, programa_id: UUID, *, titulo: str | None = None, referencia_archivo: str | None = None
    ) -> ProgramaMateria | None:
        record = await self.get(programa_id)
        if record is None:
            return None
        if titulo is not None:
            record.titulo = titulo
        if referencia_archivo is not None:
            record.referencia_archivo = referencia_archivo
        return record

    async def exists_active(
        self, *, materia_id: UUID, carrera_id: UUID, cohorte_id: UUID, titulo: str
    ) -> bool:
        result = await self.session.execute(
            select(ProgramaMateria).where(
                ProgramaMateria.tenant_id == self.tenant_id,
                ProgramaMateria.deleted_at.is_(None),
                ProgramaMateria.materia_id == materia_id,
                ProgramaMateria.carrera_id == carrera_id,
                ProgramaMateria.cohorte_id == cohorte_id,
                ProgramaMateria.titulo == titulo,
            )
        )
        return result.scalar_one_or_none() is not None
