"""Router para fechas académicas."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import ESTRUCTURA_GESTIONAR
from app.models.programas import TipoFechaAcademica
from app.schemas.programas import (
    FechaAcademicaCalendarResponse,
    FechaAcademicaCreate,
    FechaAcademicaResponse,
    FechaAcademicaUpdate,
    LMSFragmentResponse,
)
from app.services.auth import CurrentUser
from app.services.fecha_academica_service import (
    FechaAcademicaService,
    FechaNotFoundError,
    FechaValidationError,
)

router = APIRouter(prefix="/api/fechas-academicas", tags=["fechas-academicas"])

FechasGuard = Depends(require_permission(ESTRUCTURA_GESTIONAR))


def _service(db: AsyncSession, current_user: CurrentUser) -> FechaAcademicaService:
    return FechaAcademicaService(db, current_user.tenant_id)


@router.post("", response_model=FechaAcademicaResponse, status_code=status.HTTP_201_CREATED)
async def create_fecha(
    body: FechaAcademicaCreate,
    _: CurrentUser = FechasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> FechaAcademicaResponse:
    try:
        fecha = await _service(db, current_user).create_fecha(
            materia_id=body.materia_id,
            cohorte_id=body.cohorte_id,
            tipo=body.tipo,
            numero=body.numero,
            periodo=body.periodo,
            fecha=body.fecha,
            titulo=body.titulo,
        )
    except FechaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FechaValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return FechaAcademicaResponse.model_validate(fecha)


@router.get("", response_model=list[FechaAcademicaResponse])
async def list_fechas(
    _: CurrentUser = FechasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    materia_id: UUID | None = Query(default=None),
    cohorte_id: UUID | None = Query(default=None),
    tipo: TipoFechaAcademica | None = Query(default=None),
    periodo: str | None = Query(default=None),
) -> list[FechaAcademicaResponse]:
    fechas = await _service(db, current_user).list_fechas(
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        tipo=tipo,
        periodo=periodo,
    )
    return [FechaAcademicaResponse.model_validate(f) for f in fechas]


@router.get("/calendario", response_model=list[FechaAcademicaCalendarResponse])
async def list_calendario(
    _: CurrentUser = FechasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    desde: date = Query(...),
    hasta: date = Query(...),
) -> list[FechaAcademicaCalendarResponse]:
    fechas = await _service(db, current_user).list_calendario(desde=desde, hasta=hasta)
    return [FechaAcademicaCalendarResponse.model_validate(f) for f in fechas]


@router.get("/lms-fragment", response_model=LMSFragmentResponse)
async def get_lms_fragment(
    _: CurrentUser = FechasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    materia_id: UUID = Query(...),
    cohorte_id: UUID = Query(...),
) -> LMSFragmentResponse:
    contenido = await _service(db, current_user).generate_lms_fragment(
        materia_id=materia_id,
        cohorte_id=cohorte_id,
    )
    return LMSFragmentResponse(contenido=contenido)


@router.get("/{fecha_id}", response_model=FechaAcademicaResponse)
async def get_fecha(
    fecha_id: UUID,
    _: CurrentUser = FechasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> FechaAcademicaResponse:
    try:
        fecha = await _service(db, current_user).get_fecha(fecha_id)
    except FechaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FechaAcademicaResponse.model_validate(fecha)


@router.put("/{fecha_id}", response_model=FechaAcademicaResponse)
async def update_fecha(
    fecha_id: UUID,
    body: FechaAcademicaUpdate,
    _: CurrentUser = FechasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> FechaAcademicaResponse:
    try:
        fecha = await _service(db, current_user).update_fecha(
            fecha_id,
            titulo=body.titulo,
            fecha=body.fecha,
            numero=body.numero,
            periodo=body.periodo,
        )
    except FechaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FechaAcademicaResponse.model_validate(fecha)


@router.delete("/{fecha_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fecha(
    fecha_id: UUID,
    _: CurrentUser = FechasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    try:
        await _service(db, current_user).delete_fecha(fecha_id)
    except FechaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
