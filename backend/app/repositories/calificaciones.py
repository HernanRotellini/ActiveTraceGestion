"""Repositorios tenant-scoped para calificaciones y umbral de materia."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificaciones import Calificacion, OrigenCalificacion, UmbralMateria
from app.repositories.base import TenantScopedRepository

DEFAULT_UMBRAL_PCT = 60
DEFAULT_VALORES_APROBATORIOS = ["Satisfactorio", "Supera lo esperado"]


class CalificacionRepository(TenantScopedRepository[Calificacion]):
    """Acceso a calificaciones, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Calificacion, tenant_id)

    async def list_by_materia(self, materia_id: UUID) -> list[Calificacion]:
        """Lista calificaciones visibles para una materia."""
        result = await self.session.execute(
            select(Calificacion).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_by_id(self, calificacion_id: UUID) -> Calificacion | None:
        """Obtiene una calificación por id."""
        return await self.get(calificacion_id)

    async def create_batch(
        self, calificaciones: list[Calificacion]
    ) -> list[Calificacion]:
        """Inserta múltiples calificaciones en batch.

        Cada objeto debe tener ya tenant_id y demás campos asignados.
        Si algún objeto no tiene importado_at, se asigna la fecha actual.

        Args:
            calificaciones: Lista de objetos Calificacion a insertar.

        Returns:
            Lista de objetos Calificacion insertados.
        """
        now = datetime.now(UTC)
        for cal in calificaciones:
            if cal.importado_at is None:
                cal.importado_at = now
        self.session.add_all(calificaciones)
        await self.session.flush()
        return calificaciones

    async def soft_delete_by_materia(
        self, materia_id: UUID, usuario_id: UUID
    ) -> int:
        """Soft-delete calificaciones de una materia.

        Args:
            materia_id: UUID de la materia.
            usuario_id: UUID del usuario que realiza la operación.

        Returns:
            Número de registros soft-deleteados.
        """
        now = datetime.now(UTC)
        result = await self.session.execute(
            update(Calificacion)
            .where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.deleted_at.is_(None),
            )
            .values(deleted_at=now)
        )
        return result.rowcount  # type: ignore[return-value]

    async def count_by_materia(self, materia_id: UUID) -> int:
        """Cuenta calificaciones activas para una materia."""
        result = await self.session.execute(
            select(func.count()).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.materia_id == materia_id,
                Calificacion.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0

    async def exists_for_entrada_actividad(
        self, entrada_padron_id: UUID, actividad: str
    ) -> bool:
        """Verifica si existe una calificación para una entrada y actividad."""
        result = await self.session.execute(
            select(func.count()).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.entrada_padron_id == entrada_padron_id,
                Calificacion.actividad == actividad,
                Calificacion.deleted_at.is_(None),
            )
        )
        return (result.scalar() or 0) > 0

    async def list_by_entradas(
        self, entrada_ids: list[UUID]
    ) -> list[Calificacion]:
        """Lista calificaciones para un conjunto de entradas."""
        result = await self.session.execute(
            select(Calificacion).where(
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.entrada_padron_id.in_(entrada_ids),
                Calificacion.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())


class UmbralMateriaRepository(TenantScopedRepository[UmbralMateria]):
    """Acceso a umbrales de materia, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, UmbralMateria, tenant_id)

    async def get_by_asignacion(
        self, asignacion_id: UUID, materia_id: UUID
    ) -> UmbralMateria | None:
        """Retorna el umbral configurado para una asignación×materia."""
        result = await self.session.execute(
            select(UmbralMateria).where(
                UmbralMateria.tenant_id == self.tenant_id,
                UmbralMateria.asignacion_id == asignacion_id,
                UmbralMateria.materia_id == materia_id,
                UmbralMateria.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        asignacion_id: UUID,
        materia_id: UUID,
        data: dict,
    ) -> UmbralMateria:
        """Crea o actualiza el umbral para una asignación×materia.

        Args:
            asignacion_id: UUID de la asignación docente.
            materia_id: UUID de la materia.
            data: Dict con campos umbral_pct y valores_aprobatorios.
        """
        existing = await self.get_by_asignacion(asignacion_id, materia_id)
        if existing is not None:
            existing.umbral_pct = data.get("umbral_pct", existing.umbral_pct)
            existing.valores_aprobatorios = data.get(
                "valores_aprobatorios", existing.valores_aprobatorios
            )
            return existing
        record = UmbralMateria(
            tenant_id=self.tenant_id,
            asignacion_id=asignacion_id,
            materia_id=materia_id,
            umbral_pct=data.get("umbral_pct", DEFAULT_UMBRAL_PCT),
            valores_aprobatorios=data.get("valores_aprobatorios", DEFAULT_VALORES_APROBATORIOS),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def delete(self, umbral_id: UUID) -> bool:
        """Soft-delete un umbral por su id."""
        return await self.soft_delete(umbral_id)

    async def delete_by_asignacion(
        self, asignacion_id: UUID, materia_id: UUID
    ) -> bool:
        """Soft-delete el umbral para una asignación×materia."""
        existing = await self.get_by_asignacion(asignacion_id, materia_id)
        if existing is None:
            return False
        existing.deleted_at = datetime.now(UTC)
        return True

    @staticmethod
    def get_default() -> dict:
        """Retorna valores por defecto cuando no hay umbral configurado.

        Returns:
            Dict con umbral_pct=60 y valores_aprobatorios=["Satisfactorio", "Supera lo esperado"].
        """
        return {
            "umbral_pct": DEFAULT_UMBRAL_PCT,
            "valores_aprobatorios": DEFAULT_VALORES_APROBATORIOS,
        }
