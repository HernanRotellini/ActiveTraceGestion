"""Servicio de estructura académica con reglas de negocio."""

from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.estructura_academica import (
    CarreraRepository,
    CohorteRepository,
    MateriaRepository,
)


class DuplicateError(ValueError):
    """Raised when a unique constraint would be violated."""


class NotFoundError(ValueError):
    """Raised when a referenced entity is not found."""


class InactiveCarreraError(ValueError):
    """Raised when trying to create a cohorte on an inactive carrera."""


class EstructuraAcademicaService:
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._carreras = CarreraRepository(session, tenant_id)
        self._cohortes = CohorteRepository(session, tenant_id)
        self._materias = MateriaRepository(session, tenant_id)

    # ── Carrera ──────────────────────────────────────────────

    async def create_carrera(self, codigo: str, nombre: str) -> CarreraRepository:
        existing = await self._carreras.get_by_codigo(codigo)
        if existing is not None:
            raise DuplicateError(f"Carrera with codigo '{codigo}' already exists")
        return await self._carreras.create(codigo=codigo, nombre=nombre)

    async def get_carrera(self, carrera_id: UUID):
        return await self._carreras.get(carrera_id)

    async def list_carreras(self):
        return await self._carreras.list()

    async def update_carrera(self, carrera_id: UUID, *, nombre: str | None = None, estado: str | None = None):
        record = await self._carreras.update(carrera_id, nombre=nombre, estado=estado)
        if record is None:
            raise NotFoundError(f"Carrera with id '{carrera_id}' not found")
        return record

    async def delete_carrera(self, carrera_id: UUID) -> bool:
        return await self._carreras.soft_delete(carrera_id)

    # ── Cohorte ──────────────────────────────────────────────

    async def create_cohorte(self, carrera_id: UUID, nombre: str, anio: int, vig_desde: date, vig_hasta: date | None = None):
        carrera = await self._carreras.get(carrera_id)
        if carrera is None:
            raise NotFoundError(f"Carrera with id '{carrera_id}' not found")
        if carrera.estado != "activa":
            raise InactiveCarreraError("Cannot create cohorte on inactive carrera")
        existing = await self._cohortes.get_by_carrera_and_nombre(carrera_id, nombre)
        if existing is not None:
            raise DuplicateError(f"Cohorte with name '{nombre}' already exists in this carrera")
        return await self._cohortes.create(carrera_id=carrera_id, nombre=nombre, anio=anio, vig_desde=vig_desde, vig_hasta=vig_hasta)

    async def get_cohorte(self, cohorte_id: UUID):
        return await self._cohortes.get(cohorte_id)

    async def list_cohortes(self, carrera_id: UUID | None = None):
        if carrera_id is not None:
            return await self._cohortes.list_by_carrera(carrera_id)
        return await self._cohortes.list()

    async def delete_cohorte(self, cohorte_id: UUID) -> bool:
        return await self._cohortes.soft_delete(cohorte_id)

    # ── Materia ──────────────────────────────────────────────

    async def create_materia(self, codigo: str, nombre: str):
        existing = await self._materias.get_by_codigo(codigo)
        if existing is not None:
            raise DuplicateError(f"Materia with codigo '{codigo}' already exists")
        return await self._materias.create(codigo=codigo, nombre=nombre)

    async def get_materia(self, materia_id: UUID):
        return await self._materias.get(materia_id)

    async def list_materias(self):
        return await self._materias.list()

    async def update_materia(self, materia_id: UUID, *, nombre: str | None = None, estado: str | None = None):
        record = await self._materias.update(materia_id, nombre=nombre, estado=estado)
        if record is None:
            raise NotFoundError(f"Materia with id '{materia_id}' not found")
        return record

    async def delete_materia(self, materia_id: UUID) -> bool:
        return await self._materias.soft_delete(materia_id)
