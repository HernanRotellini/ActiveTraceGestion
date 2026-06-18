"""Servicio de estructura académica con reglas de negocio."""

from datetime import date
from uuid import UUID

from sqlalchemy import select
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


class InactiveCohorteError(ValueError):
    """Raised when trying to create a materia on an inactive cohorte."""


class DeleteBlockedError(ValueError):
    """Raised when business rules block a soft delete."""


class EstructuraAcademicaService:
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._carreras = CarreraRepository(session, tenant_id)
        self._cohortes = CohorteRepository(session, tenant_id)
        self._materias = MateriaRepository(session, tenant_id)

    # ── Carrera ──────────────────────────────────────────────

    async def create_carrera(
        self,
        codigo: str,
        nombre: str,
        descripcion: str | None = None,
        estado: str | None = None,
    ) -> CarreraRepository:
        existing = await self._carreras.get_by_codigo(codigo)
        if existing is not None:
            raise DuplicateError(f"Carrera with codigo '{codigo}' already exists")
        existing_name = await self._carreras.get_by_nombre(nombre)
        if existing_name is not None:
            raise DuplicateError(f"Carrera with nombre '{nombre}' already exists")
        return await self._carreras.create(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            estado=estado,
        )

    async def get_carrera(self, carrera_id: UUID):
        return await self._carreras.get(carrera_id)

    async def list_carreras(
        self,
        *,
        codigo: str | None = None,
        nombre: str | None = None,
        estado: str | None = None,
    ):
        return await self._carreras.list_filtered(codigo=codigo, nombre=nombre, estado=estado)

    async def update_carrera(self, carrera_id: UUID, *, nombre: str | None = None, codigo: str | None = None, descripcion: str | None = None, estado: str | None = None):
        if codigo is not None:
            existing = await self._carreras.get_by_codigo(codigo)
            if existing is not None and existing.id != carrera_id:
                raise DuplicateError(f"Carrera with codigo '{codigo}' already exists")
        if nombre is not None:
            existing_name = await self._carreras.get_by_nombre(nombre)
            if existing_name is not None and existing_name.id != carrera_id:
                raise DuplicateError(f"Carrera with nombre '{nombre}' already exists")
        record = await self._carreras.update(carrera_id, nombre=nombre, codigo=codigo, descripcion=descripcion, estado=estado)
        if record is None:
            raise NotFoundError(f"Carrera with id '{carrera_id}' not found")
        return record

    async def delete_carrera(self, carrera_id: UUID) -> bool:
        carrera = await self._carreras.get(carrera_id)
        if carrera is None:
            return False
        if carrera.estado == "activa":
            raise DeleteBlockedError("Cannot delete active carrera")
        cohortes_count = await self._carreras.count_cohortes(carrera_id)
        if cohortes_count > 0:
            raise DeleteBlockedError("Cannot delete carrera with associated cohortes")
        asignaciones_count = await self._carreras.count_asignaciones(carrera_id)
        if asignaciones_count > 0:
            raise DeleteBlockedError("Cannot delete carrera with associated asignaciones")
        return await self._carreras.soft_delete(carrera_id)

    # ── Cohorte ──────────────────────────────────────────────

    async def create_cohorte(
        self,
        carrera_id: UUID,
        nombre: str,
        anio: int,
        vig_desde: date,
        vig_hasta: date | None = None,
        estado: str | None = None,
    ):
        carrera = await self._carreras.get(carrera_id)
        if carrera is None:
            raise NotFoundError(f"Carrera with id '{carrera_id}' not found")
        if carrera.estado != "activa":
            raise InactiveCarreraError("Cannot create cohorte on inactive carrera")
        existing = await self._cohortes.get_by_carrera_and_nombre(carrera_id, nombre)
        if existing is not None:
            raise DuplicateError(f"Cohorte with name '{nombre}' already exists in this carrera")
        return await self._cohortes.create(
            carrera_id=carrera_id,
            nombre=nombre,
            anio=anio,
            vig_desde=vig_desde,
            vig_hasta=vig_hasta,
            estado=estado,
        )

    async def get_cohorte(self, cohorte_id: UUID):
        return await self._cohortes.get(cohorte_id)

    async def list_cohortes(self, carrera_id: UUID | None = None):
        if carrera_id is not None:
            return await self._cohortes.list_by_carrera(carrera_id)
        return await self._cohortes.list()

    async def update_cohorte(
        self,
        cohorte_id: UUID,
        *,
        nombre: str | None = None,
        anio: int | None = None,
        vig_desde: date | None = None,
        vig_hasta: date | None = None,
        vig_hasta_set: bool = False,
        estado: str | None = None,
    ):
        current = await self._cohortes.get(cohorte_id)
        if current is None:
            raise NotFoundError(f"Cohorte with id '{cohorte_id}' not found")
        if nombre is not None:
            existing = await self._cohortes.get_by_carrera_and_nombre(current.carrera_id, nombre)
            if existing is not None and existing.id != cohorte_id:
                raise DuplicateError(f"Cohorte with name '{nombre}' already exists in this carrera")
        record = await self._cohortes.update(
            cohorte_id,
            nombre=nombre,
            anio=anio,
            vig_desde=vig_desde,
            vig_hasta=vig_hasta,
            vig_hasta_set=vig_hasta_set,
            estado=estado,
        )
        if record is None:
            raise NotFoundError(f"Cohorte with id '{cohorte_id}' not found")
        return record

    async def delete_cohorte(self, cohorte_id: UUID) -> bool:
        return await self._cohortes.soft_delete(cohorte_id)

    # ── Materia ──────────────────────────────────────────────

    async def create_materia(
        self,
        codigo: str,
        nombre: str,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        carga_horaria: int = 0,
        estado: str | None = None,
    ):
        existing = await self._materias.get_by_codigo(codigo)
        if existing is not None:
            raise DuplicateError(f"Materia with codigo '{codigo}' already exists")
        if carrera_id is not None:
            carrera = await self._carreras.get(carrera_id)
            if carrera is None:
                raise NotFoundError(f"Carrera with id '{carrera_id}' not found")
            if carrera.estado != "activa":
                raise InactiveCarreraError("Cannot create materia on inactive carrera")
        if cohorte_id is not None:
            cohorte = await self._cohortes.get(cohorte_id)
            if cohorte is None:
                raise NotFoundError(f"Cohorte with id '{cohorte_id}' not found")
            if carrera_id is not None and cohorte.carrera_id != carrera_id:
                raise NotFoundError("Cohorte does not belong to selected carrera")
            if cohorte.estado != "activa":
                raise InactiveCohorteError("Cannot create materia on inactive cohorte")
        return await self._materias.create(
            codigo=codigo,
            nombre=nombre,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            carga_horaria=carga_horaria,
            estado=estado,
        )

    async def get_materia(self, materia_id: UUID):
        return await self._materias.get(materia_id)

    async def list_materias(self, carrera_id: UUID | None = None, cohorte_id: UUID | None = None):
        from app.models.estructura_academica import Carrera, Cohorte as CohorteModel, Materia as MateriaModel

        query = (
            select(MateriaModel, Carrera.nombre, CohorteModel.nombre)
            .outerjoin(Carrera, MateriaModel.carrera_id == Carrera.id)
            .outerjoin(CohorteModel, MateriaModel.cohorte_id == CohorteModel.id)
            .where(MateriaModel.tenant_id == self.tenant_id, MateriaModel.deleted_at.is_(None))
        )
        if carrera_id is not None:
            query = query.where(MateriaModel.carrera_id == carrera_id)
        if cohorte_id is not None:
            query = query.where(MateriaModel.cohorte_id == cohorte_id)

        result = await self.session.execute(query)
        rows = result.all()
        materias = []
        for materia, carrera_nombre, cohorte_nombre in rows:
            materia.carrera_nombre = carrera_nombre
            materia.cohorte_nombre = cohorte_nombre
            materias.append(materia)
        return materias

    async def update_materia(
        self,
        materia_id: UUID,
        *,
        nombre: str | None = None,
        codigo: str | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        carga_horaria: int | None = None,
        estado: str | None = None,
    ):
        if codigo is not None:
            existing = await self._materias.get_by_codigo(codigo)
            if existing is not None and existing.id != materia_id:
                raise DuplicateError(f"Materia with codigo '{codigo}' already exists")
        if carrera_id is not None:
            carrera = await self._carreras.get(carrera_id)
            if carrera is None:
                raise NotFoundError(f"Carrera with id '{carrera_id}' not found")
            if carrera.estado != "activa":
                raise InactiveCarreraError("Cannot update materia on inactive carrera")
        if cohorte_id is not None:
            cohorte = await self._cohortes.get(cohorte_id)
            if cohorte is None:
                raise NotFoundError(f"Cohorte with id '{cohorte_id}' not found")
            if carrera_id is not None and cohorte.carrera_id != carrera_id:
                raise NotFoundError("Cohorte does not belong to selected carrera")
            if cohorte.estado != "activa":
                raise InactiveCohorteError("Cannot update materia on inactive cohorte")
        record = await self._materias.update(
            materia_id,
            nombre=nombre,
            codigo=codigo,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            carga_horaria=carga_horaria,
            estado=estado,
        )
        if record is None:
            raise NotFoundError(f"Materia with id '{materia_id}' not found")
        return record

    async def delete_materia(self, materia_id: UUID) -> bool:
        return await self._materias.soft_delete(materia_id)
