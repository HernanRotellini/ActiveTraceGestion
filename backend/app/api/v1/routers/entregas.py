"""Router para entregas pendientes de corrección."""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import ENTREGAS_DETECTAR_SIN_CORREGIR
from app.schemas.analisis import (
    EntregaPendienteResponse,
    EntregasPendientesResponse,
)
from app.services.auth import CurrentUser
from app.services.analisis import AnalisisService

router = APIRouter(prefix="/api/entregas", tags=["entregas"])

EntregasGuard = Depends(require_permission(ENTREGAS_DETECTAR_SIN_CORREGIR))


@router.get(
    "/pendientes",
    response_model=EntregasPendientesResponse,
    dependencies=[EntregasGuard],
)
async def get_entregas_pendientes(
    comision_id: str | None = Query(None, description="Filtro opcional por comisión"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> EntregasPendientesResponse:
    """Lista entregas con TPs textuales sin calificar."""
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    items = await service.get_entregas_pendientes(comision=comision_id)
    return EntregasPendientesResponse(
        items=[EntregaPendienteResponse(**item) for item in items],
        total=len(items),
    )


@router.get(
    "/pendientes/exportar",
    dependencies=[EntregasGuard],
)
async def exportar_entregas_pendientes(
    comision_id: str | None = Query(None, description="Filtro opcional por comisión"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> StreamingResponse:
    """Exporta entregas pendientes como CSV."""
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    csv_content = await service.exportar_entregas_csv(comision=comision_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=entregas_pendientes.csv"},
    )
