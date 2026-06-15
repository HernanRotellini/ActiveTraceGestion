"""Repositories tenant-scoped para períodos académicos."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estructura_academica import (
    Materia,
    PeriodoAcademico,
    PeriodoFecha,
    PeriodoPrograma,
)
from app.repositories.base import TenantScopedRepository


class PeriodoAcademicoRepository(TenantScopedRepository[PeriodoAcademico]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, PeriodoAcademico, tenant_id)

    async def create(self, nombre: str, fecha_inicio, fecha_fin) -> PeriodoAcademico:
        record = PeriodoAcademico(
            tenant_id=self.tenant_id,
            nombre=nombre,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def update(self, record_id: UUID, *, nombre: str | None = None, fecha_inicio=None, fecha_fin=None) -> PeriodoAcademico | None:
        record = await self.get(record_id)
        if record is None:
            return None
        if nombre is not None:
            record.nombre = nombre
        if fecha_inicio is not None:
            record.fecha_inicio = fecha_inicio
        if fecha_fin is not None:
            record.fecha_fin = fecha_fin
        return record

    async def set_activo(self, record_id: UUID, activo: bool) -> PeriodoAcademico | None:
        record = await self.get(record_id)
        if record is None:
            return None
        record.activo = activo
        return record


class PeriodoFechaRepository:
    """Repo para fechas de período (child entity, scoped by tenant)."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id

    async def list_by_periodo(self, periodo_id: UUID) -> list[PeriodoFecha]:
        result = await self.session.execute(
            select(PeriodoFecha).where(
                PeriodoFecha.tenant_id == self.tenant_id,
                PeriodoFecha.periodo_id == periodo_id,
                PeriodoFecha.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def create(self, periodo_id: UUID, key: str, label: str, fecha) -> PeriodoFecha:
        record = PeriodoFecha(
            tenant_id=self.tenant_id,
            periodo_id=periodo_id,
            key=key,
            label=label,
            fecha=fecha,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def delete(self, fecha_id: UUID) -> bool:
        result = await self.session.execute(
            select(PeriodoFecha).where(
                PeriodoFecha.id == fecha_id,
                PeriodoFecha.tenant_id == self.tenant_id,
                PeriodoFecha.deleted_at.is_(None),
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            return False
        from datetime import UTC, datetime
        record.deleted_at = datetime.now(UTC)
        return True


class PeriodoProgramaRepository:
    """Repo para programas de período (child entity, scoped by tenant)."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id

    async def list_by_periodo(self, periodo_id: UUID) -> list[PeriodoPrograma]:
        result = await self.session.execute(
            select(PeriodoPrograma).where(
                PeriodoPrograma.tenant_id == self.tenant_id,
                PeriodoPrograma.periodo_id == periodo_id,
                PeriodoPrograma.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def create(self, periodo_id: UUID, materia_id: UUID, carrera: str, anio: int) -> PeriodoPrograma:
        record = PeriodoPrograma(
            tenant_id=self.tenant_id,
            periodo_id=periodo_id,
            materia_id=materia_id,
            carrera=carrera,
            anio=anio,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def delete(self, programa_id: UUID) -> bool:
        result = await self.session.execute(
            select(PeriodoPrograma).where(
                PeriodoPrograma.id == programa_id,
                PeriodoPrograma.tenant_id == self.tenant_id,
                PeriodoPrograma.deleted_at.is_(None),
            )
        )
        record = result.scalar_one_or_none()
        if record is None:
            return False
        from datetime import UTC, datetime
        record.deleted_at = datetime.now(UTC)
        return True
