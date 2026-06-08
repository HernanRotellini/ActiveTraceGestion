"""Repository append-only para audit-log."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id

    async def create(self, entry: AuditLog) -> AuditLog:
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def list(
        self,
        *,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        actor_id: UUID | None = None,
        accion: str | None = None,
        materia_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditLog]:
        query: Select = select(AuditLog).where(
            AuditLog.tenant_id == self.tenant_id,
        )
        if fecha_desde is not None:
            query = query.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            query = query.where(AuditLog.fecha_hora <= fecha_hasta)
        if actor_id is not None:
            query = query.where(
                (AuditLog.actor_id == actor_id) | (AuditLog.impersonado_id == actor_id),
            )
        if accion is not None:
            query = query.where(AuditLog.accion == accion)
        if materia_id is not None:
            query = query.where(AuditLog.materia_id == materia_id)
        query = query.order_by(AuditLog.fecha_hora.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        *,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        actor_id: UUID | None = None,
        accion: str | None = None,
        materia_id: UUID | None = None,
    ) -> int:
        from sqlalchemy import func

        query = select(func.count(AuditLog.id)).where(
            AuditLog.tenant_id == self.tenant_id,
        )
        if fecha_desde is not None:
            query = query.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            query = query.where(AuditLog.fecha_hora <= fecha_hasta)
        if actor_id is not None:
            query = query.where(
                (AuditLog.actor_id == actor_id) | (AuditLog.impersonado_id == actor_id),
            )
        if accion is not None:
            query = query.where(AuditLog.accion == accion)
        if materia_id is not None:
            query = query.where(AuditLog.materia_id == materia_id)
        result = await self.session.execute(query)
        return result.scalar_one()
