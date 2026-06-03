"""Router para operaciones de equipo docente."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.config import Settings
from app.core.dependencies import get_db, require_permission
from app.models.permisos import EQUIPOS_ASIGNAR
from app.schemas.asignaciones import AsignacionResponse
from app.schemas.equipos import (
    AsignacionMasivaRequest,
    CloneEquipoRequest,
    VigenciaUpdateRequest,
    VigenciaUpdateResponse,
)
from app.services.auth import CurrentUser
from app.services.equipos import EquipoService, NotFoundError

router = APIRouter(prefix="/api/equipos", tags=["equipos"])

EquiposGuard = Depends(require_permission(EQUIPOS_ASIGNAR))

settings = Settings()


@router.get("/mis-equipos", response_model=list[AsignacionResponse])
async def list_mis_equipos(
    estado: str | None = Query(default=None),
    materia_id: UUID | None = Query(default=None),
    rol: str | None = Query(default=None),
    carrera_id: UUID | None = Query(default=None),
    cohorte_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[AsignacionResponse]:
    service = EquipoService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    return await service.list_mis_equipos(
        usuario_id=current_user.user_id,
        estado=estado,
        materia_id=materia_id,
        rol=rol,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
    )


@router.post("/asignacion-masiva", response_model=list[AsignacionResponse], status_code=status.HTTP_201_CREATED)
async def asignacion_masiva(
    body: AsignacionMasivaRequest,
    _: CurrentUser = EquiposGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[AsignacionResponse]:
    service = EquipoService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    try:
        return await service.asignacion_masiva(
            usuario_ids=body.usuario_ids,
            materia_id=body.materia_id,
            carrera_id=body.carrera_id,
            cohorte_id=body.cohorte_id,
            rol=body.rol,
            desde=body.desde,
            hasta=body.hasta,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/clonar", response_model=list[AsignacionResponse], status_code=status.HTTP_201_CREATED)
async def clone_equipo(
    body: CloneEquipoRequest,
    _: CurrentUser = EquiposGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[AsignacionResponse]:
    service = EquipoService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    return await service.clone_equipo(
        origen_materia_id=body.origen.materia_id,
        origen_carrera_id=body.origen.carrera_id,
        origen_cohorte_id=body.origen.cohorte_id,
        destino_carrera_id=body.destino.carrera_id,
        destino_cohorte_id=body.destino.cohorte_id,
        destino_desde=body.destino.desde,
        destino_hasta=body.destino.hasta,
    )


@router.patch("/vigencia", response_model=VigenciaUpdateResponse)
async def update_vigencia(
    body: VigenciaUpdateRequest,
    _: CurrentUser = EquiposGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> VigenciaUpdateResponse:
    service = EquipoService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    affected = await service.update_vigencia_equipo(
        materia_id=body.materia_id,
        carrera_id=body.carrera_id,
        cohorte_id=body.cohorte_id,
        desde=body.desde,
        hasta=body.hasta,
    )
    return VigenciaUpdateResponse(asignaciones_afectadas=affected)


@router.get("/exportar")
async def export_equipo_csv(
    materia_id: UUID = Query(...),
    carrera_id: UUID = Query(...),
    cohorte_id: UUID = Query(...),
    _: CurrentUser = EquiposGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> StreamingResponse:
    service = EquipoService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    content = await service.export_equipo_csv(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
    )
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=equipo.csv"},
    )
