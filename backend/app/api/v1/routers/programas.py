"""Router para programas de materia."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import ESTRUCTURA_GESTIONAR
from app.schemas.programas import (
    ProgramaMateriaCreate,
    ProgramaMateriaResponse,
    ProgramaMateriaUpdate,
)
from app.services.auth import CurrentUser
from app.services.programa_service import (
    ProgramaNotFoundError,
    ProgramaService,
    ProgramaValidationError,
)

router = APIRouter(prefix="/api/programas", tags=["programas"])

ProgramasGuard = Depends(require_permission(ESTRUCTURA_GESTIONAR))


def _service(db: AsyncSession, current_user: CurrentUser) -> ProgramaService:
    return ProgramaService(db, current_user.tenant_id)


@router.post("", response_model=ProgramaMateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_programa(
    body: ProgramaMateriaCreate,
    _: CurrentUser = ProgramasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ProgramaMateriaResponse:
    try:
        programa = await _service(db, current_user).create_programa(
            materia_id=body.materia_id,
            carrera_id=body.carrera_id,
            cohorte_id=body.cohorte_id,
            titulo=body.titulo,
            referencia_archivo=body.referencia_archivo,
        )
    except ProgramaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProgramaValidationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return ProgramaMateriaResponse.model_validate(programa)


@router.get("", response_model=list[ProgramaMateriaResponse])
async def list_programas(
    _: CurrentUser = ProgramasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    materia_id: UUID | None = Query(default=None),
    carrera_id: UUID | None = Query(default=None),
    cohorte_id: UUID | None = Query(default=None),
) -> list[ProgramaMateriaResponse]:
    programas = await _service(db, current_user).list_programas(
        materia_id=materia_id, carrera_id=carrera_id, cohorte_id=cohorte_id
    )
    return [ProgramaMateriaResponse.model_validate(p) for p in programas]


@router.get("/{programa_id}", response_model=ProgramaMateriaResponse)
async def get_programa(
    programa_id: UUID,
    _: CurrentUser = ProgramasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ProgramaMateriaResponse:
    try:
        programa = await _service(db, current_user).get_programa(programa_id)
    except ProgramaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ProgramaMateriaResponse.model_validate(programa)


@router.put("/{programa_id}", response_model=ProgramaMateriaResponse)
async def update_programa(
    programa_id: UUID,
    body: ProgramaMateriaUpdate,
    _: CurrentUser = ProgramasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ProgramaMateriaResponse:
    try:
        programa = await _service(db, current_user).update_programa(
            programa_id,
            titulo=body.titulo,
            referencia_archivo=body.referencia_archivo,
        )
    except ProgramaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ProgramaMateriaResponse.model_validate(programa)


@router.delete("/{programa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_programa(
    programa_id: UUID,
    _: CurrentUser = ProgramasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    try:
        await _service(db, current_user).delete_programa(programa_id)
    except ProgramaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
