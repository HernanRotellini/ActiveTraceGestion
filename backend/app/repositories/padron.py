"""Repositorio tenant-scoped para padrón de alumnos versionado."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.padron import EntradaPadron, VersionPadron
from app.repositories.base import TenantScopedRepository


class VersionPadronRepository(TenantScopedRepository[VersionPadron]):
    """Acceso a versiones de padrón, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, VersionPadron, tenant_id)

    async def get_activa(self, materia_id: UUID, cohorte_id: UUID) -> VersionPadron | None:
        """Retorna la versión activa para una materia×cohorte."""
        result = await self.session.execute(
            select(VersionPadron).where(
                VersionPadron.tenant_id == self.tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.cohorte_id == cohorte_id,
                VersionPadron.activa.is_(True),
                VersionPadron.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def desactivar_por_materia_y_cohorte(self, materia_id: UUID, cohorte_id: UUID) -> int:
        """Desactiva todas las versiones activas de una materia×cohorte.

        Returns:
            Número de versiones desactivadas.
        """
        result = await self.session.execute(
            update(VersionPadron)
            .where(
                VersionPadron.tenant_id == self.tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.cohorte_id == cohorte_id,
                VersionPadron.activa.is_(True),
                VersionPadron.deleted_at.is_(None),
            )
            .values(activa=False)
        )
        return result.rowcount  # type: ignore[return-value]

    async def listar_por_materia(
        self, materia_id: UUID, *, page: int = 1, size: int = 20
    ) -> tuple[list[VersionPadron], int]:
        """Lista versiones de padrón para una materia, paginado."""
        base_query = select(VersionPadron).where(
            VersionPadron.tenant_id == self.tenant_id,
            VersionPadron.materia_id == materia_id,
            VersionPadron.deleted_at.is_(None),
        )
        count_result = await self.session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar() or 0
        offset = (page - 1) * size
        result = await self.session.execute(
            base_query.order_by(VersionPadron.cargado_at.desc()).offset(offset).limit(size)
        )
        return list(result.scalars().all()), total  # type: ignore[return-value]

    async def crear_version(
        self,
        materia_id: UUID,
        cohorte_id: UUID,
        cargado_por: UUID,
    ) -> VersionPadron:
        """Crea una nueva versión de padrón.

        Desactiva la versión activa previa antes de crear la nueva.
        """
        await self.desactivar_por_materia_y_cohorte(materia_id, cohorte_id)
        version = VersionPadron(
            tenant_id=self.tenant_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            cargado_por=cargado_por,
            activa=True,
        )
        self.session.add(version)
        await self.session.flush()
        return version


class EntradaPadronRepository(TenantScopedRepository[EntradaPadron]):
    """Acceso a entradas de padrón, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, EntradaPadron, tenant_id)

    async def bulk_insert(self, entradas: list[EntradaPadron]) -> int:
        """Inserta múltiples entradas de padrón en batch.

        Args:
            entradas: Lista de objetos EntradaPadron (ya construidos con tenant_id).

        Returns:
            Número de entradas insertadas.
        """
        self.session.add_all(entradas)
        await self.session.flush()
        return len(entradas)

    async def contar_por_version(self, version_id: UUID) -> int:
        """Cuenta entradas activas para una versión."""
        result = await self.session.execute(
            select(func.count()).where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.version_id == version_id,
                EntradaPadron.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0

    async def vaciar_por_usuario_y_materia(
        self, usuario_id: UUID, materia_id: UUID
    ) -> int:
        """Soft-delete entradas de padrón creadas por un usuario para una materia.

        Sigue RN-04: scope (usuario_id × materia_id). No afecta datos de otros usuarios.

        Returns:
            Número de versiones soft-deleteadas.
        """
        now = datetime.now(UTC)
        result = await self.session.execute(
            update(VersionPadron)
            .where(
                VersionPadron.tenant_id == self.tenant_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.cargado_por == usuario_id,
                VersionPadron.deleted_at.is_(None),
            )
            .values(deleted_at=now)
        )
        return result.rowcount  # type: ignore[return-value]
