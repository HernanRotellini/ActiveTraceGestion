"""Repository de agregaciones para panel de auditoría y métricas."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.permisos import COMUNICACION_APROBAR_ACTION, COMUNICACION_CANCELAR, COMUNICACION_ENVIAR_ACTION
from app.repositories.audit_log import AuditLogRepository


COMUNICACION_ACCIONES = {COMUNICACION_ENVIAR_ACTION, COMUNICACION_APROBAR_ACTION, COMUNICACION_CANCELAR}


class PanelAuditoriaRepository:
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._audit_repo = AuditLogRepository(session, tenant_id)

    def _apply_base_filters(
        self,
        query: Select,
        *,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_id: UUID | None = None,
        materia_ids_scope: list[UUID] | None = None,
    ) -> Select:
        query = query.where(AuditLog.tenant_id == self.tenant_id)
        if fecha_desde is not None:
            query = query.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            query = query.where(AuditLog.fecha_hora <= fecha_hasta)
        if materia_id is not None:
            query = query.where(AuditLog.materia_id == materia_id)
        elif materia_ids_scope is not None:
            query = query.where(AuditLog.materia_id.in_(materia_ids_scope))
        return query

    async def acciones_por_dia(
        self,
        *,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_id: UUID | None = None,
        materia_ids_scope: list[UUID] | None = None,
    ) -> list[dict]:
        fecha_trunc = func.date_trunc("day", AuditLog.fecha_hora).label("fecha")
        query = select(fecha_trunc, func.count(AuditLog.id).label("total"))
        query = self._apply_base_filters(
            query,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_id=materia_id,
            materia_ids_scope=materia_ids_scope,
        )
        query = query.group_by(fecha_trunc).order_by(fecha_trunc.asc())
        result = await self.session.execute(query)
        return [{"fecha": row.fecha, "total": row.total} for row in result.all()]

    async def comunicaciones_por_docente(
        self,
        *,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_id: UUID | None = None,
        materia_ids_scope: list[UUID] | None = None,
    ) -> list[dict]:
        query = select(
            AuditLog.actor_id.label("docente_id"),
            AuditLog.accion,
            func.count(AuditLog.id).label("total"),
        )
        query = self._apply_base_filters(
            query,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_id=materia_id,
            materia_ids_scope=materia_ids_scope,
        )
        query = query.where(AuditLog.accion.in_(COMUNICACION_ACCIONES))
        query = query.group_by(AuditLog.actor_id, AuditLog.accion).order_by(
            AuditLog.actor_id, AuditLog.accion
        )
        result = await self.session.execute(query)
        return [{"docente_id": row.docente_id, "accion": row.accion, "total": row.total} for row in result.all()]

    async def interacciones_por_docente_materia(
        self,
        *,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        actor_id: UUID | None = None,
        materia_ids_scope: list[UUID] | None = None,
    ) -> list[dict]:
        query = select(
            AuditLog.actor_id.label("docente_id"),
            AuditLog.materia_id,
            AuditLog.accion,
            func.count(AuditLog.id).label("total"),
        )
        query = self._apply_base_filters(
            query,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_ids_scope=materia_ids_scope,
        )
        if actor_id is not None:
            query = query.where(AuditLog.actor_id == actor_id)
        query = query.group_by(AuditLog.actor_id, AuditLog.materia_id, AuditLog.accion).order_by(
            AuditLog.actor_id, AuditLog.materia_id, AuditLog.accion
        )
        result = await self.session.execute(query)
        return [
            {"docente_id": row.docente_id, "materia_id": row.materia_id, "accion": row.accion, "total": row.total}
            for row in result.all()
        ]

    async def ultimas_acciones(
        self,
        *,
        limit: int = 200,
        offset: int = 0,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_ids_scope: list[UUID] | None = None,
    ) -> list[AuditLog]:
        query = select(AuditLog)
        query = self._apply_base_filters(
            query,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_ids_scope=materia_ids_scope,
        )
        query = query.order_by(AuditLog.fecha_hora.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
