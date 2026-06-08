"""Router del panel de auditoría y métricas."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, get_panel_auditoria_service, require_permission
from app.models.permisos import AUDITORIA_VER
from app.schemas.audit import AuditLogResponse
from app.schemas.panel_auditoria import (
    AccionesPorDiaListResponse,
    AccionesPorDiaResponse,
    ComunicacionesPorDocenteListResponse,
    ComunicacionesPorDocenteResponse,
    InteraccionesListResponse,
    InteraccionesResponse,
    UltimasAccionesListResponse,
    UltimasAccionesResponse,
)
from app.services.auth import CurrentUser
from app.services.panel_auditoria import PanelAuditoriaService

router = APIRouter(prefix="/api/v1/auditoria", tags=["auditoria"])


@router.get("/panel/acciones-por-dia", response_model=AccionesPorDiaListResponse)
async def acciones_por_dia(
    _: CurrentUser = Depends(require_permission(AUDITORIA_VER)),
    service: PanelAuditoriaService = Depends(get_panel_auditoria_service),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    materia_id: UUID | None = Query(default=None),
) -> AccionesPorDiaListResponse:
    items = await service.get_acciones_por_dia(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        materia_id=materia_id,
    )
    return AccionesPorDiaListResponse(items=[AccionesPorDiaResponse(**row) for row in items])


@router.get("/panel/comunicaciones-por-docente", response_model=ComunicacionesPorDocenteListResponse)
async def comunicaciones_por_docente(
    _: CurrentUser = Depends(require_permission(AUDITORIA_VER)),
    service: PanelAuditoriaService = Depends(get_panel_auditoria_service),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    materia_id: UUID | None = Query(default=None),
) -> ComunicacionesPorDocenteListResponse:
    items = await service.get_comunicaciones_por_docente(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        materia_id=materia_id,
    )
    return ComunicacionesPorDocenteListResponse(
        items=[ComunicacionesPorDocenteResponse(**row) for row in items]
    )


@router.get("/panel/interacciones-por-docente-materia", response_model=InteraccionesListResponse)
async def interacciones_por_docente_materia(
    _: CurrentUser = Depends(require_permission(AUDITORIA_VER)),
    service: PanelAuditoriaService = Depends(get_panel_auditoria_service),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    actor_id: UUID | None = Query(default=None),
) -> InteraccionesListResponse:
    items = await service.get_interacciones_por_docente_materia(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        actor_id=actor_id,
    )
    return InteraccionesListResponse(items=[InteraccionesResponse(**row) for row in items])


@router.get("/panel/ultimas-acciones", response_model=UltimasAccionesListResponse)
async def ultimas_acciones(
    _: CurrentUser = Depends(require_permission(AUDITORIA_VER)),
    service: PanelAuditoriaService = Depends(get_panel_auditoria_service),
    max_results: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> UltimasAccionesListResponse:
    items = await service.get_ultimas_acciones(
        limit=max_results,
        offset=offset,
    )
    return UltimasAccionesListResponse(
        items=[UltimasAccionesResponse.model_validate(e) for e in items]
    )
