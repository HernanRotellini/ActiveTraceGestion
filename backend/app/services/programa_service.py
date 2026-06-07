"""Servicio de programas de materia."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estructura_academica import Carrera, Cohorte, Materia
from app.models.programas import ProgramaMateria
from app.repositories.programa_repository import ProgramaMateriaRepository


class ProgramaNotFoundError(ValueError):
    """Programa no encontrado en el tenant actual."""


class ProgramaValidationError(ValueError):
    """Validación fallida para el programa."""


class ProgramaService:
    """Orquesta programas de materia sin acceder directamente a la DB."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._repo = ProgramaMateriaRepository(session, tenant_id)

    async def _validate_context(
        self, *, materia_id: UUID, carrera_id: UUID, cohorte_id: UUID
    ) -> None:
        """Verificar que materia, carrera, cohorte existan y pertenezcan al tenant."""
        result = await self.session.execute(
            select(Materia).where(
                Materia.id == materia_id,
                Materia.tenant_id == self.tenant_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise ProgramaNotFoundError(f"Materia {materia_id} no encontrada en el tenant")

        result = await self.session.execute(
            select(Carrera).where(
                Carrera.id == carrera_id,
                Carrera.tenant_id == self.tenant_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise ProgramaNotFoundError(f"Carrera {carrera_id} no encontrada en el tenant")

        result = await self.session.execute(
            select(Cohorte).where(
                Cohorte.id == cohorte_id,
                Cohorte.tenant_id == self.tenant_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise ProgramaNotFoundError(f"Cohorte {cohorte_id} no encontrada en el tenant")

    async def create_programa(
        self,
        *,
        materia_id: UUID,
        carrera_id: UUID,
        cohorte_id: UUID,
        titulo: str,
        referencia_archivo: str,
    ) -> ProgramaMateria:
        await self._validate_context(materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id)
        if await self._repo.exists_active(
            materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id, titulo=titulo
        ):
            raise ProgramaValidationError(
                "Ya existe un programa activo con ese título para el mismo contexto académico"
            )
        return await self._repo.create(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            titulo=titulo,
            referencia_archivo=referencia_archivo,
        )

    async def list_programas(
        self,
        *,
        materia_id: UUID | None = None,
        carrera_id: UUID | None = None,
        cohorte_id: UUID | None = None,
    ) -> list[ProgramaMateria]:
        return await self._repo.list_filtered(
            materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id
        )

    async def get_programa(self, programa_id: UUID) -> ProgramaMateria:
        programa = await self._repo.get(programa_id)
        if programa is None:
            raise ProgramaNotFoundError(f"Programa {programa_id} no encontrado")
        return programa

    async def update_programa(
        self,
        programa_id: UUID,
        *,
        titulo: str | None = None,
        referencia_archivo: str | None = None,
    ) -> ProgramaMateria:
        programa = await self._repo.update(
            programa_id, titulo=titulo, referencia_archivo=referencia_archivo
        )
        if programa is None:
            raise ProgramaNotFoundError(f"Programa {programa_id} no encontrado")
        return programa

    async def delete_programa(self, programa_id: UUID) -> None:
        if not await self._repo.soft_delete(programa_id):
            raise ProgramaNotFoundError(f"Programa {programa_id} no encontrado")
