"""Servicio central de auditoría."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.permisos import (
    CALIFICACIONES_IMPORTAR_ACTION,
    COMUNICACION_ENVIAR_ACTION,
    COMUNICACION_APROBAR_ACTION,
    COMUNICACION_CANCELAR,
    PADRON_CARGAR,
    ASIGNACION_MODIFICAR,
    LIQUIDACION_CERRAR,
    IMPERSONACION_INICIAR,
    IMPERSONACION_FINALIZAR,
    ANALISIS_EXPORTAR,
    ANALISIS_CONSULTAR,
)
from app.repositories.audit_log import AuditLogRepository
from app.services.auth import CurrentUser


class AuditService:
    def __init__(
        self,
        db: AsyncSession,
        current_user: CurrentUser,
        ip: str,
        user_agent: str,
    ) -> None:
        self.db = db
        self.current_user = current_user
        self.ip = ip
        self.user_agent = user_agent
        self._repo = AuditLogRepository(db, current_user.tenant_id)

    async def log(
        self,
        accion: str,
        detalle: dict | None = None,
        filas_afectadas: int | None = None,
        materia_id: UUID | None = None,
    ) -> AuditLog:
        if self.current_user.impersonator_id is not None:
            actor_id = self.current_user.impersonator_id
            impersonado_id = self.current_user.user_id
        else:
            actor_id = self.current_user.user_id
            impersonado_id = None

        entry = AuditLog(
            tenant_id=self.current_user.tenant_id,
            actor_id=actor_id,
            impersonado_id=impersonado_id,
            materia_id=materia_id,
            accion=accion,
            detalle=detalle or {},
            filas_afectadas=filas_afectadas or 0,
            ip=self.ip,
            user_agent=self.user_agent,
        )
        return await self._repo.create(entry)

    async def log_calificaciones_importar(
        self,
        total_filas: int,
        detalle_extra: dict | None = None,
        materia_id: UUID | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=CALIFICACIONES_IMPORTAR_ACTION,
            detalle=detalle_extra,
            filas_afectadas=total_filas,
            materia_id=materia_id,
        )

    async def log_padron_cargar(
        self,
        total_filas: int,
        detalle_extra: dict | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=PADRON_CARGAR,
            detalle=detalle_extra,
            filas_afectadas=total_filas,
        )

    async def log_comunicacion_enviar(
        self,
        detalle_extra: dict | None = None,
        materia_id: UUID | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=COMUNICACION_ENVIAR_ACTION,
            detalle=detalle_extra,
            materia_id=materia_id,
        )

    async def log_comunicacion_aprobar(
        self,
        detalle_extra: dict | None = None,
        materia_id: UUID | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=COMUNICACION_APROBAR_ACTION,
            detalle=detalle_extra,
            materia_id=materia_id,
        )

    async def log_comunicacion_cancelar(
        self,
        detalle_extra: dict | None = None,
        materia_id: UUID | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=COMUNICACION_CANCELAR,
            detalle=detalle_extra,
            materia_id=materia_id,
        )

    async def log_asignacion_modificar(
        self,
        detalle_extra: dict | None = None,
        materia_id: UUID | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=ASIGNACION_MODIFICAR,
            detalle=detalle_extra,
            materia_id=materia_id,
        )

    async def log_liquidacion_cerrar(
        self,
        detalle_extra: dict | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=LIQUIDACION_CERRAR,
            detalle=detalle_extra,
        )

    async def log_impersonacion_iniciar(
        self,
        detalle_extra: dict | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=IMPERSONACION_INICIAR,
            detalle=detalle_extra,
        )

    async def log_impersonacion_finalizar(
        self,
        detalle_extra: dict | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=IMPERSONACION_FINALIZAR,
            detalle=detalle_extra,
        )

    async def log_analisis_exportar(
        self,
        detalle_extra: dict | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=ANALISIS_EXPORTAR,
            detalle=detalle_extra,
        )

    async def log_analisis_consultar(
        self,
        detalle_extra: dict | None = None,
    ) -> AuditLog:
        return await self.log(
            accion=ANALISIS_CONSULTAR,
            detalle=detalle_extra,
        )
