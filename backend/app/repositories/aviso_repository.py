"""Repositorio tenant-scoped para el modelo Aviso.

Incluye lógica de filtrado por visibilidad según alcance,
vigencia y perfil del usuario.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import AcknowledgmentAviso, Aviso
from app.repositories.base import TenantScopedRepository


class AvisoRepository(TenantScopedRepository[Aviso]):
    """Acceso a datos de avisos, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Aviso, tenant_id)

    async def listar_visibles(
        self,
        roles: list[str],
        materia_ids: list[UUID] | None = None,
        cohorte_ids: list[UUID] | None = None,
    ) -> list[Aviso]:
        """Lista avisos visibles para un usuario según su perfil.

        Filtros automáticos:
        - activo = true
        - inicio_en <= NOW()
        - fin_en IS NULL OR fin_en >= NOW()
        - alcance coincide con rol, materias o cohortes del usuario
        """
        now = datetime.now(UTC)
        stmt = (
            select(Aviso)
            .where(
                Aviso.tenant_id == self.tenant_id,
                Aviso.activo.is_(True),
                Aviso.deleted_at.is_(None),
                Aviso.inicio_en <= now,
            )
            .where(
                (Aviso.fin_en.is_(None)) | (Aviso.fin_en >= now),
            )
        )

        # Construir condiciones de alcance
        conditions = [Aviso.alcance == "Global"]

        if roles:
            conditions.append(
                (Aviso.alcance == "PorRol") & Aviso.rol_destino.in_(roles)
            )

        if materia_ids:
            conditions.append(
                (Aviso.alcance == "PorMateria") & Aviso.materia_id.in_(materia_ids)
            )

        if cohorte_ids:
            conditions.append(
                (Aviso.alcance == "PorCohorte") & Aviso.cohorte_id.in_(cohorte_ids)
            )

        stmt = stmt.where(*([__import__("sqlalchemy").or_(*conditions)] if len(conditions) > 1 else conditions))
        stmt = stmt.order_by(Aviso.orden.asc(), Aviso.inicio_en.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def listar_admin(
        self,
        alcance: str | None = None,
        severidad: str | None = None,
        activo: bool | None = None,
    ) -> list[Aviso]:
        """Lista todos los avisos del tenant (incluyendo inactivos y fuera de vigencia)."""
        stmt = select(Aviso).where(
            Aviso.tenant_id == self.tenant_id,
            Aviso.deleted_at.is_(None),
        )
        if alcance is not None:
            stmt = stmt.where(Aviso.alcance == alcance)
        if severidad is not None:
            stmt = stmt.where(Aviso.severidad == severidad)
        if activo is not None:
            stmt = stmt.where(Aviso.activo.is_(activo))

        stmt = stmt.order_by(Aviso.orden.asc(), Aviso.inicio_en.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def crear(self, aviso: Aviso) -> Aviso:
        """Crea un nuevo aviso."""
        self.session.add(aviso)
        await self.session.flush()
        return aviso

    async def actualizar(self, aviso_id: UUID, datos: dict) -> Aviso | None:
        """Actualiza campos de un aviso existente."""
        stmt = (
            update(Aviso)
            .where(
                Aviso.id == aviso_id,
                Aviso.tenant_id == self.tenant_id,
                Aviso.deleted_at.is_(None),
            )
            .values(**datos)
            .returning(Aviso)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def desactivar(self, aviso_id: UUID) -> bool:
        """Soft delete: marca activo = false."""
        stmt = (
            update(Aviso)
            .where(
                Aviso.id == aviso_id,
                Aviso.tenant_id == self.tenant_id,
                Aviso.deleted_at.is_(None),
            )
            .values(activo=False)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0

    async def obtener_stats(self, aviso_id: UUID) -> dict:
        """Retorna contadores derivados de AcknowledgmentAviso."""
        from sqlalchemy import func

        # Total de acks
        count_stmt = (
            select(func.count())
            .select_from(AcknowledgmentAviso)
            .where(
                AcknowledgmentAviso.aviso_id == aviso_id,
                AcknowledgmentAviso.tenant_id == self.tenant_id,
                AcknowledgmentAviso.deleted_at.is_(None),
            )
        )
        total_result = await self.session.execute(count_stmt)
        total_acks = total_result.scalar() or 0

        return {"total_acks": total_acks}
