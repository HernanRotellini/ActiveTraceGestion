"""Router para calificaciones y umbral de aprobación."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import CALIFICACIONES_IMPORTAR
from app.schemas.calificaciones import (
    CalificacionListResponse,
    CalificacionResponse,
    CompletionReportResponse,
    ImportConfirmRequest,
    ImportConfirmResponse,
    ImportPreviewResponse,
    PosibleEntregaSinCorregir,
    UmbralMateriaCreate,
    UmbralMateriaResponse,
)
from app.services.auth import CurrentUser
from app.services.calificaciones import (
    CalificacionError,
    CalificacionService,
    PreviewExpiredError,
    UmbralMateriaService,
)
from app.services.lms_parser import LmsParseError

router = APIRouter(prefix="/api/calificaciones", tags=["calificaciones"])

CalifGuard = Depends(require_permission(CALIFICACIONES_IMPORTAR))


# ── Import Preview ──────────────────────────────────────────────


@router.post(
    "/import/preview",
    response_model=ImportPreviewResponse,
    status_code=status.HTTP_200_OK,
)
async def import_preview(
    materia_id: UUID = Query(...),
    cohorte_id: UUID = Query(...),
    archivo: UploadFile = ...,
    _: CurrentUser = CalifGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ImportPreviewResponse:
    """Paso 1: Subir archivo LMS, obtener preview con actividades detectadas."""
    service = CalificacionService(db, current_user.tenant_id, current_user.user_id)
    contenido = await archivo.read()
    filename = archivo.filename or "upload"
    try:
        result = await service.importar_grades(materia_id, cohorte_id, filename, contenido)
    except LmsParseError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except CalificacionError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return ImportPreviewResponse(
        preview_token=result["preview_token"],
        materia_id=result["materia_id"],
        cohorte_id=result["cohorte_id"],
        actividades=result["actividades"],
        total_rows=result["total_rows"],
        alumnos_match=result["alumnos_match"],
        alumnos_no_match=result["alumnos_no_match"],
    )


# ── Import Confirm ──────────────────────────────────────────────


@router.post(
    "/import/confirm",
    response_model=ImportConfirmResponse,
    status_code=status.HTTP_200_OK,
)
async def import_confirm(
    body: ImportConfirmRequest,
    _: CurrentUser = CalifGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ImportConfirmResponse:
    """Paso 2: Confirmar import con preview_token y activity_ids."""
    service = CalificacionService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.confirmar_import(body.preview_token, body.actividad_ids)
    except PreviewExpiredError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except CalificacionError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return ImportConfirmResponse(
        materia_id=result["materia_id"],
        cohorte_id=result["cohorte_id"],
        registros_creados=result["registros_creados"],
        actividades_importadas=result["actividades_importadas"],
    )


# ── Completion Report ───────────────────────────────────────────


@router.post(
    "/completion-report",
    response_model=CompletionReportResponse,
    status_code=status.HTTP_200_OK,
)
async def completion_report(
    materia_id: UUID = Query(...),
    cohorte_id: UUID = Query(...),
    archivo: UploadFile = ...,
    _: CurrentUser = CalifGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> CompletionReportResponse:
    """Detecta entregas textuales finalizadas sin calificación."""
    service = CalificacionService(db, current_user.tenant_id, current_user.user_id)
    contenido = await archivo.read()
    filename = archivo.filename or "upload"
    try:
        result = await service.importar_completion_report(
            materia_id, cohorte_id, filename, contenido
        )
    except (LmsParseError, CalificacionError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return CompletionReportResponse(
        materia_id=result["materia_id"],
        cohorte_id=result["cohorte_id"],
        posibles_entregas_sin_corregir=[
            PosibleEntregaSinCorregir(**item)
            for item in result["posibles_entregas_sin_corregir"]
        ],
    )


# ── Umbral ──────────────────────────────────────────────────────


@router.get("/umbral", response_model=UmbralMateriaResponse)
async def get_umbral(
    materia_id: UUID = Query(...),
    asignacion_id: UUID = Query(...),
    _: CurrentUser = CalifGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> UmbralMateriaResponse:
    """Obtiene umbral configurado o default."""
    service = UmbralMateriaService(db, current_user.tenant_id)
    umbral = await service.obtener(asignacion_id, materia_id)
    # Si no hay umbral configurado, los defaults no tienen id real
    # ni timestamps — se reemplazan con placeholders
    from datetime import UTC, datetime
    now_val = datetime.now(UTC)
    return UmbralMateriaResponse(
        id=umbral.get("id") or UUID(int=0),
        tenant_id=umbral.get("tenant_id", current_user.tenant_id),
        asignacion_id=UUID(umbral["asignacion_id"]),
        materia_id=UUID(umbral["materia_id"]),
        umbral_pct=umbral["umbral_pct"],
        valores_aprobatorios=umbral["valores_aprobatorios"],
        created_at=umbral.get("created_at") or now_val,
        updated_at=umbral.get("updated_at") or now_val,
        deleted_at=umbral.get("deleted_at"),
    )


@router.put("/umbral", response_model=UmbralMateriaResponse)
async def set_umbral(
    materia_id: UUID = Query(...),
    asignacion_id: UUID = Query(...),
    body: UmbralMateriaCreate = ...,
    _: CurrentUser = CalifGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> UmbralMateriaResponse:
    """Configura o actualiza el umbral de una materia."""
    service = UmbralMateriaService(db, current_user.tenant_id)
    try:
        umbral = await service.configurar(
            asignacion_id=asignacion_id,
            materia_id=materia_id,
            umbral_pct=body.umbral_pct,
            valores_aprobatorios=body.valores_aprobatorios,
        )
    except CalificacionError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return UmbralMateriaResponse.model_validate(umbral)


# ── List Calificaciones ─────────────────────────────────────────


@router.get("", response_model=CalificacionListResponse)
async def list_calificaciones(
    materia_id: UUID = Query(...),
    _: CurrentUser = CalifGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> CalificacionListResponse:
    """Lista calificaciones de una materia."""
    service = CalificacionService(db, current_user.tenant_id, current_user.user_id)
    result = await service.listar_calificaciones(materia_id)
    return CalificacionListResponse(
        items=[CalificacionResponse.model_validate(c) for c in result["items"]],
        total=result["total"],
    )
