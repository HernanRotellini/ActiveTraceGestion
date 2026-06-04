"""Router para el módulo de guardias tutoriales."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import ENCUENTROS_GESTIONAR, GUARDIAS_REGISTRAR
from app.schemas.guardia import GuardiaCreate, GuardiaResponse, GuardiaUpdate
from app.services.auth import CurrentUser
from app.services.guardia_service import GuardiaError, GuardiaService

router = APIRouter(prefix="/api/v1/guardias", tags=["guardias"])

RegistrarGuard = Depends(require_permission(GUARDIAS_REGISTRAR))
GestionarGuard = Depends(require_permission(ENCUENTROS_GESTIONAR))


@router.post("", response_model=GuardiaResponse, status_code=status.HTTP_201_CREATED)
async def registrar_guardia(
    body: GuardiaCreate,
    _: CurrentUser = RegistrarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> GuardiaResponse:
    """Registra una guardia tutorial."""
    service = GuardiaService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.registrar(
            asignacion_id=body.asignacion_id,
            materia_id=body.materia_id,
            carrera_id=body.carrera_id,
            cohorte_id=body.cohorte_id,
            dia=body.dia,
            horario=body.horario,
            estado=body.estado,
            comentarios=body.comentarios,
        )
    except GuardiaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return GuardiaResponse(**result)


@router.get("", response_model=list[GuardiaResponse])
async def listar_guardias(
    materia_id: UUID | None = Query(None),
    carrera_id: UUID | None = Query(None),
    cohorte_id: UUID | None = Query(None),
    estado: str | None = Query(None),
    _: CurrentUser = RegistrarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[GuardiaResponse]:
    """Lista guardias del tenant con filtros."""
    service = GuardiaService(db, current_user.tenant_id, current_user.user_id)
    result = await service.listar(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        estado=estado,
    )
    return [GuardiaResponse(**item) for item in result]


@router.patch("/{guardia_id}", response_model=GuardiaResponse)
async def actualizar_estado_guardia(
    guardia_id: UUID,
    body: GuardiaUpdate,
    _: CurrentUser = RegistrarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> GuardiaResponse:
    """Actualiza estado y/o comentarios de una guardia."""
    service = GuardiaService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.actualizar_estado(
            guardia_id=guardia_id,
            estado=body.estado or "Pendiente",
            comentarios=body.comentarios,
        )
    except GuardiaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return GuardiaResponse(**result)


@router.get("/exportar-csv")
async def exportar_guardias_csv(
    materia_id: UUID | None = Query(None),
    carrera_id: UUID | None = Query(None),
    cohorte_id: UUID | None = Query(None),
    estado: str | None = Query(None),
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> StreamingResponse:
    """Exporta guardias filtradas a CSV."""
    service = GuardiaService(db, current_user.tenant_id, current_user.user_id)
    csv_content = await service.exportar_csv(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        estado=estado,
    )
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=guardias.csv"},
    )
