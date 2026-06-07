"""Repositorio tenant-scoped para fechas académicas."""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.programas import FechaAcademica, TipoFechaAcademica
from app.repositories.base import TenantScopedRepository


class FechaAcademicaRepository(TenantScopedRepository[FechaAcademica]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, FechaAcademica, tenant_id)

    async def create(
        self,
        *,
        materia_id: UUID,
        cohorte_id: UUID,
        tipo: TipoFechaAcademica,
        numero: int,
        periodo: str,
        fecha: date,
        titulo: str,
    ) -> FechaAcademica:
        record = FechaAcademica(
            tenant_id=self.tenant_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=tipo,
            numero=numero,
            periodo=periodo,
            fecha=fecha,
            titulo=titulo,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_by_materia(self, materia_id: UUID) -> list[FechaAcademica]:
        result = await self.session.execute(
            select(FechaAcademica).where(
                FechaAcademica.tenant_id == self.tenant_id,
                FechaAcademica.deleted_at.is_(None),
                FechaAcademica.materia_id == materia_id,
            )
        )
        return list(result.scalars().all())

    async def list_by_cohorte(self, cohorte_id: UUID) -> list[FechaAcademica]:
        result = await self.session.execute(
            select(FechaAcademica).where(
                FechaAcademica.tenant_id == self.tenant_id,
                FechaAcademica.deleted_at.is_(None),
                FechaAcademica.cohorte_id == cohorte_id,
            )
        )
        return list(result.scalars().all())

    async def list_by_tipo(self, tipo: TipoFechaAcademica) -> list[FechaAcademica]:
        result = await self.session.execute(
            select(FechaAcademica).where(
                FechaAcademica.tenant_id == self.tenant_id,
                FechaAcademica.deleted_at.is_(None),
                FechaAcademica.tipo == tipo,
            )
        )
        return list(result.scalars().all())

    async def list_by_periodo(self, periodo: str) -> list[FechaAcademica]:
        result = await self.session.execute(
            select(FechaAcademica).where(
                FechaAcademica.tenant_id == self.tenant_id,
                FechaAcademica.deleted_at.is_(None),
                FechaAcademica.periodo == periodo,
            )
        )
        return list(result.scalars().all())

    async def list_filtered(
        self,
        *,
        materia_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        tipo: TipoFechaAcademica | None = None,
        periodo: str | None = None,
    ) -> list[FechaAcademica]:
        where = [
            FechaAcademica.tenant_id == self.tenant_id,
            FechaAcademica.deleted_at.is_(None),
        ]
        if materia_id is not None:
            where.append(FechaAcademica.materia_id == materia_id)
        if cohorte_id is not None:
            where.append(FechaAcademica.cohorte_id == cohorte_id)
        if tipo is not None:
            where.append(FechaAcademica.tipo == tipo)
        if periodo is not None:
            where.append(FechaAcademica.periodo == periodo)
        result = await self.session.execute(select(FechaAcademica).where(*where))
        return list(result.scalars().all())

    async def list_by_date_range(self, *, desde: date, hasta: date) -> list[FechaAcademica]:
        result = await self.session.execute(
            select(FechaAcademica).where(
                FechaAcademica.tenant_id == self.tenant_id,
                FechaAcademica.deleted_at.is_(None),
                FechaAcademica.fecha >= desde,
                FechaAcademica.fecha <= hasta,
            )
        )
        return list(result.scalars().all())

    async def list_for_calendar(self, *, desde: date, hasta: date) -> list[FechaAcademica]:
        result = await self.session.execute(
            select(FechaAcademica)
            .where(
                FechaAcademica.tenant_id == self.tenant_id,
                FechaAcademica.deleted_at.is_(None),
                FechaAcademica.fecha >= desde,
                FechaAcademica.fecha <= hasta,
            )
            .order_by(FechaAcademica.fecha)
        )
        return list(result.scalars().all())

    async def update(
        self,
        fecha_id: UUID,
        *,
        titulo: str | None = None,
        fecha: date | None = None,
        numero: int | None = None,
        periodo: str | None = None,
    ) -> FechaAcademica | None:
        record = await self.get(fecha_id)
        if record is None:
            return None
        if titulo is not None:
            record.titulo = titulo
        if fecha is not None:
            record.fecha = fecha
        if numero is not None:
            record.numero = numero
        if periodo is not None:
            record.periodo = periodo
        return record

    async def exists_active_duplicate(
        self,
        *,
        materia_id: UUID,
        cohorte_id: UUID,
        tipo: TipoFechaAcademica,
        numero: int,
        periodo: str,
    ) -> bool:
        result = await self.session.execute(
            select(FechaAcademica).where(
                FechaAcademica.tenant_id == self.tenant_id,
                FechaAcademica.deleted_at.is_(None),
                FechaAcademica.materia_id == materia_id,
                FechaAcademica.cohorte_id == cohorte_id,
                FechaAcademica.tipo == tipo,
                FechaAcademica.numero == numero,
                FechaAcademica.periodo == periodo,
            )
        )
        return result.scalar_one_or_none() is not None
