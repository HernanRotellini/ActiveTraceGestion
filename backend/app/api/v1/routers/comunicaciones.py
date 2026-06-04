"""Router para el módulo de comunicaciones."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import COMUNICACION_APROBAR, COMUNICACION_ENVIAR
from app.schemas.comunicacion import (
    AccionResponse,
    ComunicacionDetail,
    EnvioMasivoRequest,
    EnvioMasivoResponse,
    LoteDetalleResponse,
    LoteResumen,
    LotesListResponse,
    PreviewRequest,
    PreviewResponse,
)
from app.services.auth import CurrentUser
from app.services.comunicacion_service import ComunicacionError, ComunicacionService

router = APIRouter(prefix="/api/comunicaciones", tags=["comunicaciones"])

EnviarGuard = Depends(require_permission(COMUNICACION_ENVIAR))
AprobarGuard = Depends(require_permission(COMUNICACION_APROBAR))


@router.post("/preview", response_model=PreviewResponse)
async def preview(
    body: PreviewRequest,
    _: CurrentUser = EnviarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PreviewResponse:
    """Preview de comunicación con sustitución de variables (RN-16)."""
    service = ComunicacionService(db, current_user.tenant_id, current_user.user_id)
    result = await service.preview(body.asunto, body.cuerpo, body.variables)
    return PreviewResponse(**result)


@router.post("/enviar", response_model=EnvioMasivoResponse, status_code=status.HTTP_201_CREATED)
async def enviar_masivo(
    body: EnvioMasivoRequest,
    _: CurrentUser = EnviarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> EnvioMasivoResponse:
    """Encola comunicaciones por alumno atrasado de una materia (F3.2)."""
    service = ComunicacionService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.enviar_masivo(body.materia_id, body.asunto, body.cuerpo)
    except ComunicacionError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return EnvioMasivoResponse(**result)


@router.get("/lotes", response_model=LotesListResponse)
async def listar_lotes(
    _: CurrentUser = EnviarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> LotesListResponse:
    """Lista lotes con estados agregados."""
    service = ComunicacionService(db, current_user.tenant_id, current_user.user_id)
    result = await service.listar_lotes()
    return LotesListResponse(
        items=[LoteResumen(**item) for item in result["items"]],
        total=result["total"],
    )


@router.get("/lotes/{lote_id}", response_model=LoteDetalleResponse)
async def detalle_lote(
    lote_id: UUID,
    _: CurrentUser = EnviarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> LoteDetalleResponse:
    """Detalle de comunicaciones en un lote."""
    service = ComunicacionService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.detalle_lote(lote_id)
    except ComunicacionError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return LoteDetalleResponse(
        lote_id=result["lote_id"],
        materia_id=result["materia_id"],
        comunicaciones=[ComunicacionDetail(**item) for item in result["comunicaciones"]],
    )


@router.post("/lotes/{lote_id}/aprobar", response_model=AccionResponse)
async def aprobar_lote(
    lote_id: UUID,
    _: CurrentUser = AprobarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AccionResponse:
    """Aprueba un lote de comunicaciones (RN-17)."""
    service = ComunicacionService(db, current_user.tenant_id, current_user.user_id)
    try:
        afectados = await service.aprobar_lote(lote_id)
    except ComunicacionError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return AccionResponse(mensaje="Lote aprobado", afectados=afectados)


@router.post("/lotes/{lote_id}/cancelar", response_model=AccionResponse)
async def cancelar_lote(
    lote_id: UUID,
    _: CurrentUser = AprobarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AccionResponse:
    """Cancela un lote de comunicaciones."""
    service = ComunicacionService(db, current_user.tenant_id, current_user.user_id)
    afectados = await service.cancelar_lote(lote_id)
    return AccionResponse(mensaje="Lote cancelado", afectados=afectados)


@router.post("/{comunicacion_id}/cancelar", response_model=AccionResponse)
async def cancelar_comunicacion(
    comunicacion_id: UUID,
    _: CurrentUser = AprobarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AccionResponse:
    """Cancela una comunicación individual."""
    service = ComunicacionService(db, current_user.tenant_id, current_user.user_id)
    ok = await service.cancelar_comunicacion(comunicacion_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede cancelar: comunicación no encontrada o no está Pendiente",
        )
    return AccionResponse(mensaje="Comunicación cancelada", afectados=1)
