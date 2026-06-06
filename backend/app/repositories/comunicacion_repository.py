"""Repositorio tenant-scoped para comunicaciones."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.repositories.base import TenantScopedRepository


class ComunicacionRepository(TenantScopedRepository[Comunicacion]):
    """Acceso a Comunicaciones, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Comunicacion, tenant_id)

    async def create_batch(self, comunicaciones: list[Comunicacion]) -> list[Comunicacion]:
        """Inserta múltiples comunicaciones en batch."""
        self.session.add_all(comunicaciones)
        await self.session.flush()
        return comunicaciones

    async def list_lotes(self) -> list[dict]:
        """Lista lotes con estados agregados para el tenant actual."""
        stmt = (
            select(
                Comunicacion.lote_id,
                Comunicacion.materia_id,
                func.count().label("total"),
                func.sum(
                    func.cast(Comunicacion.estado == EstadoComunicacion.PENDIENTE.value, func.Integer)
                ).label("pendientes"),
                func.sum(
                    func.cast(Comunicacion.estado == EstadoComunicacion.ENVIADO.value, func.Integer)
                ).label("enviados"),
                func.sum(
                    func.cast(Comunicacion.estado == EstadoComunicacion.ERROR.value, func.Integer)
                ).label("errores"),
                func.sum(
                    func.cast(Comunicacion.estado == EstadoComunicacion.CANCELADO.value, func.Integer)
                ).label("cancelados"),
                func.min(Comunicacion.created_at).label("created_at"),
            )
            .where(
                Comunicacion.tenant_id == self.tenant_id,
                Comunicacion.deleted_at.is_(None),
            )
            .group_by(Comunicacion.lote_id, Comunicacion.materia_id)
            .order_by(func.min(Comunicacion.created_at).desc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            {
                "lote_id": row.lote_id,
                "materia_id": row.materia_id,
                "total": row.total or 0,
                "pendientes": row.pendientes or 0,
                "enviados": row.enviados or 0,
                "errores": row.errores or 0,
                "cancelados": row.cancelados or 0,
                "created_at": row.created_at,
            }
            for row in rows
        ]

    async def detalle_lote(self, lote_id: UUID) -> list[Comunicacion]:
        """Retorna todas las comunicaciones activas de un lote."""
        result = await self.session.execute(
            select(Comunicacion).where(
                Comunicacion.tenant_id == self.tenant_id,
                Comunicacion.lote_id == lote_id,
                Comunicacion.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def pendientes_para_procesar(self) -> list[Comunicacion]:
        """Retorna comunicaciones Pendiente (sin filtro de aprobación).

        El worker decide si puede procesarlas según la config del tenant.
        """
        result = await self.session.execute(
            select(Comunicacion).where(
                Comunicacion.tenant_id == self.tenant_id,
                Comunicacion.estado == EstadoComunicacion.PENDIENTE,
                Comunicacion.deleted_at.is_(None),
            )
            .order_by(Comunicacion.created_at.asc())
            .limit(100)
        )
        return list(result.scalars().all())

    async def transicionar_estado(self, comunicacion_id: UUID, nuevo_estado: EstadoComunicacion) -> Comunicacion | None:
        """Actualiza el estado de una comunicación."""
        com = await self.get(comunicacion_id)
        if com is None:
            return None
        com.transicionar(nuevo_estado)
        if nuevo_estado == EstadoComunicacion.ENVIADO:
            com.enviado_at = datetime.now(UTC)
        return com

    async def transicionar_lote(self, lote_id: UUID, nuevo_estado: EstadoComunicacion) -> int:
        """Transiciona todas las comunicaciones Pendiente de un lote.

        Returns:
            Número de registros afectados.
        """
        if nuevo_estado not in (EstadoComunicacion.ENVIANDO, EstadoComunicacion.CANCELADO):
            raise ValueError(f"No se puede transicionar un lote completo a {nuevo_estado.value}")

        result = await self.session.execute(
            update(Comunicacion)
            .where(
                Comunicacion.tenant_id == self.tenant_id,
                Comunicacion.lote_id == lote_id,
                Comunicacion.estado == EstadoComunicacion.PENDIENTE,
                Comunicacion.deleted_at.is_(None),
            )
            .values(estado=nuevo_estado)
        )
        return result.rowcount  # type: ignore[return-value]

    async def aprobar_lote(self, lote_id: UUID) -> int:
        """Aprueba un lote: Pendiente → Enviando (RN-17)."""
        return await self.transicionar_lote(lote_id, EstadoComunicacion.ENVIANDO)

    async def cancelar_lote(self, lote_id: UUID) -> int:
        """Cancela un lote: Pendiente → Cancelado."""
        return await self.transicionar_lote(lote_id, EstadoComunicacion.CANCELADO)

    async def cancelar_comunicacion(self, comunicacion_id: UUID) -> bool:
        """Cancela una comunicación individual: Pendiente → Cancelado."""
        com = await self.get(comunicacion_id)
        if com is None or com.estado != EstadoComunicacion.PENDIENTE:
            return False
        com.transicionar(EstadoComunicacion.CANCELADO)
        return True
