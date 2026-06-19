"""Servicio de períodos académicos con reglas de negocio."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.periodos_academicos import (
    PeriodoAcademicoRepository,
    PeriodoFechaRepository,
    PeriodoProgramaRepository,
)


class DuplicatePeriodoError(ValueError):
    """Raised when trying to activate a periodo but another is already active."""


class NotFoundError(ValueError):
    """Raised when a referenced entity is not found."""


class InvalidPeriodoDatesError(ValueError):
    """Raised when fecha_fin is before fecha_inicio."""


class DeleteBlockedError(ValueError):
    """Raised when a periodo has dependent setup data."""


class PeriodoAcademicoService:
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._repo = PeriodoAcademicoRepository(session, tenant_id)
        self._fechas = PeriodoFechaRepository(session, tenant_id)
        self._programas = PeriodoProgramaRepository(session, tenant_id)

    # ── Periodo CRUD ─────────────────────────────────────────

    async def create(self, nombre: str, fecha_inicio, fecha_fin):
        if fecha_fin < fecha_inicio:
            raise InvalidPeriodoDatesError("fecha_fin must be greater than or equal to fecha_inicio")
        return await self._repo.create(
            nombre=nombre,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

    async def get(self, periodo_id: UUID):
        return await self._repo.get(periodo_id)

    async def list_all(self):
        return await self._repo.list()

    async def update(self, periodo_id: UUID, *, nombre: str | None = None, fecha_inicio=None, fecha_fin=None):
        current = await self._repo.get(periodo_id)
        if current is None:
            raise NotFoundError(f"PeriodoAcademico with id '{periodo_id}' not found")
        next_inicio = fecha_inicio if fecha_inicio is not None else current.fecha_inicio
        next_fin = fecha_fin if fecha_fin is not None else current.fecha_fin
        if next_fin < next_inicio:
            raise InvalidPeriodoDatesError("fecha_fin must be greater than or equal to fecha_inicio")
        record = await self._repo.update(periodo_id, nombre=nombre, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        if record is None:
            raise NotFoundError(f"PeriodoAcademico with id '{periodo_id}' not found")
        return record

    async def delete(self, periodo_id: UUID) -> bool:
        if await self._repo.has_dependencias(periodo_id):
            raise DeleteBlockedError("Cannot delete periodo with associated fechas or programas")
        return await self._repo.soft_delete(periodo_id)

    async def activar(self, periodo_id: UUID):
        """Activa un periodo y desactiva cualquier otro activo."""
        # Desactivar todos los demás
        all_periodos = await self._repo.list()
        for p in all_periodos:
            if p.id != periodo_id and p.activo:
                await self._repo.set_activo(p.id, False)
        # Activar el solicitado
        record = await self._repo.set_activo(periodo_id, True)
        if record is None:
            raise NotFoundError(f"PeriodoAcademico with id '{periodo_id}' not found")
        return record

    async def desactivar(self, periodo_id: UUID):
        record = await self._repo.set_activo(periodo_id, False)
        if record is None:
            raise NotFoundError(f"PeriodoAcademico with id '{periodo_id}' not found")
        return record

    # ── Fechas ───────────────────────────────────────────────

    async def list_fechas(self, periodo_id: UUID) -> list:
        return await self._fechas.list_by_periodo(periodo_id)

    async def add_fecha(self, periodo_id: UUID, key: str, label: str, fecha):
        return await self._fechas.create(periodo_id, key, label, fecha)

    async def remove_fecha(self, fecha_id: UUID) -> bool:
        return await self._fechas.delete(fecha_id)

    # ── Programas ────────────────────────────────────────────

    async def list_programas(self, periodo_id: UUID) -> list:
        return await self._programas.list_by_periodo(periodo_id)

    async def add_programa(self, periodo_id: UUID, materia_id: UUID, carrera: str, anio: int):
        return await self._programas.create(periodo_id, materia_id, carrera, anio)

    async def remove_programa(self, programa_id: UUID) -> bool:
        return await self._programas.delete(programa_id)
