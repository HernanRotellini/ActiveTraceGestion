"""Repositories tenant-scoped para estructura académica."""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estructura_academica import Carrera, Cohorte, Materia
from app.repositories.base import TenantScopedRepository


class CarreraRepository(TenantScopedRepository[Carrera]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Carrera, tenant_id)

    async def get_by_codigo(self, codigo: str) -> Carrera | None:
        result = await self.session.execute(
            select(Carrera).where(
                Carrera.tenant_id == self.tenant_id,
                Carrera.deleted_at.is_(None),
                Carrera.codigo == codigo,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, codigo: str, nombre: str, descripcion: str | None = None) -> Carrera:
        record = Carrera(tenant_id=self.tenant_id, codigo=codigo, nombre=nombre, descripcion=descripcion or "")
        self.session.add(record)
        await self.session.flush()
        return record

    async def update(self, carrera_id: UUID, *, nombre: str | None = None, codigo: str | None = None, descripcion: str | None = None, estado: str | None = None) -> Carrera | None:
        record = await self.get(carrera_id)
        if record is None:
            return None
        if nombre is not None:
            record.nombre = nombre
        if codigo is not None:
            record.codigo = codigo
        if descripcion is not None:
            record.descripcion = descripcion
        if estado is not None:
            record.estado = estado
        return record


class CohorteRepository(TenantScopedRepository[Cohorte]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Cohorte, tenant_id)

    async def get_by_carrera_and_nombre(self, carrera_id: UUID, nombre: str) -> Cohorte | None:
        result = await self.session.execute(
            select(Cohorte).where(
                Cohorte.tenant_id == self.tenant_id,
                Cohorte.deleted_at.is_(None),
                Cohorte.carrera_id == carrera_id,
                Cohorte.nombre == nombre,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_carrera(self, carrera_id: UUID) -> list[Cohorte]:
        result = await self.session.execute(
            select(Cohorte).where(
                Cohorte.tenant_id == self.tenant_id,
                Cohorte.deleted_at.is_(None),
                Cohorte.carrera_id == carrera_id,
            )
        )
        return list(result.scalars().all())

    async def update(self, cohorte_id: UUID, *, nombre: str | None = None, anio: int | None = None, vig_desde: date | None = None, vig_hasta: date | None = None) -> Cohorte | None:
        record = await self.get(cohorte_id)
        if record is None:
            return None
        if nombre is not None:
            record.nombre = nombre
        if anio is not None:
            record.anio = anio
        if vig_desde is not None:
            record.vig_desde = vig_desde
        if vig_hasta is not None:
            record.vig_hasta = vig_hasta
        return record

    async def create(self, carrera_id: UUID, nombre: str, anio: int, vig_desde: date, vig_hasta: date | None = None) -> Cohorte:
        record = Cohorte(
            tenant_id=self.tenant_id,
            carrera_id=carrera_id,
            nombre=nombre,
            anio=anio,
            vig_desde=vig_desde,
            vig_hasta=vig_hasta,
        )
        self.session.add(record)
        await self.session.flush()
        return record


class MateriaRepository(TenantScopedRepository[Materia]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Materia, tenant_id)

    async def get_by_codigo(self, codigo: str) -> Materia | None:
        result = await self.session.execute(
            select(Materia).where(
                Materia.tenant_id == self.tenant_id,
                Materia.deleted_at.is_(None),
                Materia.codigo == codigo,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, codigo: str, nombre: str) -> Materia:
        record = Materia(tenant_id=self.tenant_id, codigo=codigo, nombre=nombre)
        self.session.add(record)
        await self.session.flush()
        return record

    async def update(self, materia_id: UUID, *, nombre: str | None = None, codigo: str | None = None, carga_horaria: int | None = None, estado: str | None = None) -> Materia | None:
        record = await self.get(materia_id)
        if record is None:
            return None
        if nombre is not None:
            record.nombre = nombre
        if codigo is not None:
            record.codigo = codigo
        if carga_horaria is not None:
            record.carga_horaria = carga_horaria
        if estado is not None:
            record.estado = estado
        return record
