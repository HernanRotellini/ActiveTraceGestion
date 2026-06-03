"""Router para ABM de Asignaciones."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.config import Settings
from app.core.dependencies import get_db, require_permission
from app.models.permisos import EQUIPOS_ASIGNAR
from app.schemas.asignaciones import AsignacionCreate, AsignacionResponse, AsignacionUpdate
from app.services.asignaciones import (
    AsignacionService,
    NotFoundError,
    ResponsableNotFoundError,
)
from app.services.auth import CurrentUser

router = APIRouter(prefix="/api/asignaciones", tags=["asignaciones"])

AsignacionesGuard = Depends(require_permission(EQUIPOS_ASIGNAR))

settings = Settings()  # type: ignore[call-arg]


@router.post("", response_model=AsignacionResponse, status_code=status.HTTP_201_CREATED)
async def create_asignacion(
    body: AsignacionCreate,
    _: CurrentUser = AsignacionesGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AsignacionResponse:
    service = AsignacionService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    try:
        asignacion = await service.create_asignacion(**body.model_dump())
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResponsableNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return AsignacionResponse.model_validate(asignacion)


@router.get("", response_model=list[AsignacionResponse])
async def list_asignaciones(
    materia_id: UUID | None = Query(default=None),
    usuario_id: UUID | None = Query(default=None),
    rol: str | None = Query(default=None),
    _: CurrentUser = AsignacionesGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[AsignacionResponse]:
    service = AsignacionService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    asignaciones = await service.list_asignaciones(materia_id=materia_id, usuario_id=usuario_id, rol=rol)
    return [AsignacionResponse.model_validate(a) for a in asignaciones]


@router.get("/{asignacion_id}", response_model=AsignacionResponse)
async def get_asignacion(
    asignacion_id: UUID,
    _: CurrentUser = AsignacionesGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AsignacionResponse:
    service = AsignacionService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    asignacion = await service.get_asignacion(asignacion_id)
    if asignacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignacion not found")
    return AsignacionResponse.model_validate(asignacion)


@router.patch("/{asignacion_id}", response_model=AsignacionResponse)
async def update_asignacion(
    asignacion_id: UUID,
    body: AsignacionUpdate,
    _: CurrentUser = AsignacionesGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AsignacionResponse:
    service = AsignacionService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    try:
        asignacion = await service.update_asignacion(asignacion_id, **body.model_dump(exclude_none=True))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResponsableNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return AsignacionResponse.model_validate(asignacion)


@router.delete("/{asignacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asignacion(
    asignacion_id: UUID,
    _: CurrentUser = AsignacionesGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    service = AsignacionService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    deleted = await service.delete_asignacion(asignacion_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignacion not found")
