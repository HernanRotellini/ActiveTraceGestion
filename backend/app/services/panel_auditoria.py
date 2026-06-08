"""Servicio de panel de auditoría y métricas con scope (propio)."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.usuarios_asignaciones import Asignacion
from app.repositories.panel_auditoria import PanelAuditoriaRepository
from app.services.auth import CurrentUser


ROLES_SCOPE_TOTAL = {"ADMIN", "FINANZAS"}
ROL_COORDINADOR = "COORDINADOR"


class PanelAuditoriaService:
    def __init__(self, db: AsyncSession, current_user: CurrentUser) -> None:
        self.db = db
        self.current_user = current_user
        self._repo = PanelAuditoriaRepository(db, current_user.tenant_id)

    async def _get_materias_scope(self) -> list[UUID] | None:
        if any(r in ROLES_SCOPE_TOTAL for r in self.current_user.roles):
            return None
        if ROL_COORDINADOR in self.current_user.roles:
            stmt = select(Asignacion.materia_id).where(
                Asignacion.tenant_id == self.current_user.tenant_id,
                Asignacion.usuario_id == self.current_user.user_id,
                Asignacion.rol == ROL_COORDINADOR,
                Asignacion.materia_id.isnot(None),
            )
            result = await self.db.execute(stmt)
            materia_ids = [row[0] for row in result.all() if row[0] is not None]
            return materia_ids
        return None

    async def get_acciones_por_dia(
        self,
        *,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_id: UUID | None = None,
    ) -> list[dict]:
        materia_ids_scope = await self._get_materias_scope()
        if materia_id is not None and materia_ids_scope is not None:
            if materia_id not in materia_ids_scope:
                return []
            materia_ids_scope = None
        return await self._repo.acciones_por_dia(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_id=materia_id if (materia_id is not None or materia_ids_scope is None) else None,
            materia_ids_scope=materia_ids_scope,
        )

    async def get_comunicaciones_por_docente(
        self,
        *,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_id: UUID | None = None,
    ) -> list[dict]:
        materia_ids_scope = await self._get_materias_scope()
        if materia_id is not None and materia_ids_scope is not None:
            if materia_id not in materia_ids_scope:
                return []
            materia_ids_scope = None
        return await self._repo.comunicaciones_por_docente(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_id=materia_id if (materia_id is not None or materia_ids_scope is None) else None,
            materia_ids_scope=materia_ids_scope,
        )

    async def get_interacciones_por_docente_materia(
        self,
        *,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        actor_id: UUID | None = None,
    ) -> list[dict]:
        materia_ids_scope = await self._get_materias_scope()
        return await self._repo.interacciones_por_docente_materia(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            actor_id=actor_id,
            materia_ids_scope=materia_ids_scope,
        )

    async def get_ultimas_acciones(
        self,
        *,
        limit: int = 200,
        offset: int = 0,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> list[AuditLog]:
        materia_ids_scope = await self._get_materias_scope()
        return await self._repo.ultimas_acciones(
            limit=limit,
            offset=offset,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_ids_scope=materia_ids_scope,
        )
