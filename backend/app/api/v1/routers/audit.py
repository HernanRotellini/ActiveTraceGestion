"""Router de consulta del audit-log."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_audit_service, get_current_user, get_db, require_permission
from app.models.permisos import AUDITORIA_VER
from app.repositories.audit_log import AuditLogRepository
from app.schemas.audit import AuditLogListResponse, AuditLogResponse
from app.services.auth import CurrentUser
from app.services.audit import AuditService

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    _: CurrentUser = Depends(require_permission(AUDITORIA_VER)),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    actor_id: UUID | None = Query(default=None),
    accion: str | None = Query(default=None),
    materia_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> AuditLogListResponse:
    repo = AuditLogRepository(db, current_user.tenant_id)
    items = await repo.list(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        actor_id=actor_id,
        accion=accion,
        materia_id=materia_id,
        limit=limit,
        offset=offset,
    )
    total = await repo.count(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        actor_id=actor_id,
        accion=accion,
        materia_id=materia_id,
    )
    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(e) for e in items],
        total=total,
    )
