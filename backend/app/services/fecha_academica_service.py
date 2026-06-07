"""Servicio de fechas académicas y generación de fragmento LMS."""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estructura_academica import Cohorte, Materia
from app.models.programas import FechaAcademica, TipoFechaAcademica
from app.repositories.fecha_academica_repository import FechaAcademicaRepository


class FechaNotFoundError(ValueError):
    """Fecha académica no encontrada en el tenant actual."""


class FechaValidationError(ValueError):
    """Validación fallida para la fecha académica."""


class FechaAcademicaService:
    """Orquesta fechas académicas sin acceder directamente a la DB."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._repo = FechaAcademicaRepository(session, tenant_id)

    async def _validate_context(self, *, materia_id: UUID, cohorte_id: UUID) -> None:
        result = await self.session.execute(
            select(Materia).where(
                Materia.id == materia_id,
                Materia.tenant_id == self.tenant_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise FechaNotFoundError(f"Materia {materia_id} no encontrada en el tenant")

        result = await self.session.execute(
            select(Cohorte).where(
                Cohorte.id == cohorte_id,
                Cohorte.tenant_id == self.tenant_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise FechaNotFoundError(f"Cohorte {cohorte_id} no encontrada en el tenant")

    async def create_fecha(
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
        await self._validate_context(materia_id=materia_id, cohorte_id=cohorte_id)
        if await self._repo.exists_active_duplicate(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=tipo,
            numero=numero,
            periodo=periodo,
        ):
            raise FechaValidationError(
                "Ya existe una fecha académica activa con el mismo contexto, tipo, número y período"
            )
        return await self._repo.create(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=tipo,
            numero=numero,
            periodo=periodo,
            fecha=fecha,
            titulo=titulo,
        )

    async def list_fechas(
        self,
        *,
        materia_id: UUID | None = None,
        cohorte_id: UUID | None = None,
        tipo: TipoFechaAcademica | None = None,
        periodo: str | None = None,
    ) -> list[FechaAcademica]:
        return await self._repo.list_filtered(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=tipo,
            periodo=periodo,
        )

    async def list_calendario(
        self, *, desde: date, hasta: date
    ) -> list[FechaAcademica]:
        return await self._repo.list_for_calendar(desde=desde, hasta=hasta)

    async def get_fecha(self, fecha_id: UUID) -> FechaAcademica:
        fecha = await self._repo.get(fecha_id)
        if fecha is None:
            raise FechaNotFoundError(f"Fecha académica {fecha_id} no encontrada")
        return fecha

    async def update_fecha(
        self,
        fecha_id: UUID,
        *,
        titulo: str | None = None,
        fecha: date | None = None,
        numero: int | None = None,
        periodo: str | None = None,
    ) -> FechaAcademica:
        fecha = await self._repo.update(
            fecha_id, titulo=titulo, fecha=fecha, numero=numero, periodo=periodo
        )
        if fecha is None:
            raise FechaNotFoundError(f"Fecha académica {fecha_id} no encontrada")
        return fecha

    async def delete_fecha(self, fecha_id: UUID) -> None:
        if not await self._repo.soft_delete(fecha_id):
            raise FechaNotFoundError(f"Fecha académica {fecha_id} no encontrada")

    async def generate_lms_fragment(
        self, *, materia_id: UUID, cohorte_id: UUID
    ) -> str:
        """Generate deterministic HTML/text fragment for LMS."""
        fechas = await self._repo.list_filtered(
            materia_id=materia_id, cohorte_id=cohorte_id
        )
        fechas.sort(key=lambda f: f.fecha)
        if not fechas:
            return "No hay fechas académicas programadas."
        lines = [
            "<table><thead><tr><th>Tipo</th><th>Nº</th><th>Título</th><th>Fecha</th></tr></thead><tbody>"
        ]
        for f in fechas:
            lines.append(
                f"<tr><td>{f.tipo.value}</td><td>{f.numero}</td><td>{f.titulo}</td><td>{f.fecha.isoformat()}</td></tr>"
            )
        lines.append("</tbody></table>")
        return "\n".join(lines)
