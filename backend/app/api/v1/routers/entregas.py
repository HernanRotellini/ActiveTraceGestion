"""Router para entregas pendientes de corrección."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.config import Settings
from app.core.dependencies import get_db, require_permission
from app.models.permisos import ATRASADOS_VER
from app.schemas.analisis import (
    EntregaPendienteResponse,
    EntregasPendientesResponse,
)
from app.services.asignaciones import AsignacionService
from app.services.auth import CurrentUser
from app.services.analisis import AnalisisService, ROLES_ENTREGAS_GLOBALES

router = APIRouter(prefix="/api/entregas", tags=["entregas"])

EntregasGuard = Depends(require_permission(ATRASADOS_VER))


async def _materias_permitidas(
    db: AsyncSession,
    current_user: CurrentUser,
) -> list[UUID] | None:
    if any(role in ROLES_ENTREGAS_GLOBALES for role in current_user.roles):
        return None

    asignacion_service = AsignacionService(
        db,
        current_user.tenant_id,
        Settings().ENCRYPTION_KEY,  # type: ignore[call-arg]
    )
    usuario_id = await asignacion_service.get_usuario_id_by_email(current_user.email)
    if usuario_id is None:
        return []

    asignaciones = await asignacion_service.list_mis_comisiones(usuario_id)
    return sorted(
        {
            asignacion.materia_id
            for asignacion in asignaciones
            if asignacion.materia_id is not None
        },
        key=str,
    )


@router.get(
    "/pendientes",
    response_model=EntregasPendientesResponse,
    dependencies=[EntregasGuard],
)
async def get_entregas_pendientes(
    comision: str | None = Query(None, description="Filtro opcional por comisión"),
    comision_id: str | None = Query(None, description="Filtro legado por comisión"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> EntregasPendientesResponse:
    """Lista entregas con TPs textuales sin calificar."""
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    materia_ids = await _materias_permitidas(db, current_user)
    filtro_comision = comision or comision_id
    items = await service.get_entregas_pendientes(
        comision=filtro_comision,
        materia_ids=materia_ids,
    )
    return EntregasPendientesResponse(
        items=[EntregaPendienteResponse(**item) for item in items],
        total=len(items),
    )


@router.get(
    "/pendientes/exportar",
    dependencies=[EntregasGuard],
)
async def exportar_entregas_pendientes(
    comision: str | None = Query(None, description="Filtro opcional por comisión"),
    comision_id: str | None = Query(None, description="Filtro legado por comisión"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> StreamingResponse:
    """Exporta entregas pendientes como CSV."""
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    materia_ids = await _materias_permitidas(db, current_user)
    filtro_comision = comision or comision_id
    csv_content = await service.exportar_entregas_csv(
        comision=filtro_comision,
        materia_ids=materia_ids,
    )
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=entregas_pendientes.csv"},
    )
