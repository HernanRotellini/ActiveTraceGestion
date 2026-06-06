"""Router para análisis de calificaciones y reportes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import ATRASADOS_VER
from app.schemas.analisis import (
    AtrasadosResponse,
    MonitorItem,
    MonitorResponse,
    NotaFinalItem,
    NotasFinalesResponse,
    RankingItem,
    RankingResponse,
    ReportesRapidosResponse,
)
from app.services.auth import CurrentUser
from app.services.analisis import AnalisisService

router = APIRouter(prefix="/api/analisis", tags=["analisis"])

Guard = Depends(require_permission(ATRASADOS_VER))


@router.get(
    "/atrasados/{materia_id}",
    response_model=list[AtrasadosResponse],
    dependencies=[Guard],
)
async def get_atrasados(
    materia_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[AtrasadosResponse]:
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    items = await service.compute_atrasados(materia_id)
    return [AtrasadosResponse(**item) for item in items]


@router.get(
    "/ranking/{materia_id}",
    response_model=RankingResponse,
    dependencies=[Guard],
)
async def get_ranking(
    materia_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> RankingResponse:
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    result = await service.compute_ranking(materia_id)
    return RankingResponse(
        items=[RankingItem(**item) for item in result["items"]],
        total=result["total"],
    )


@router.get(
    "/reportes/{materia_id}",
    response_model=ReportesRapidosResponse,
    dependencies=[Guard],
)
async def get_reportes_rapidos(
    materia_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ReportesRapidosResponse:
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    result = await service.compute_reportes_rapidos(materia_id)
    return ReportesRapidosResponse(**result)


@router.get(
    "/notas-finales/{materia_id}",
    response_model=NotasFinalesResponse,
    dependencies=[Guard],
)
async def get_notas_finales(
    materia_id: UUID,
    actividades: str = Query(..., description="Actividades separadas por coma"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> NotasFinalesResponse:
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    act_list = [a.strip() for a in actividades.split(",") if a.strip()]
    result = await service.compute_notas_finales(materia_id, act_list)
    return NotasFinalesResponse(
        items=[NotaFinalItem(**item) for item in result["items"]],
        total=result["total"],
    )


@router.get(
    "/exportar-tps/{materia_id}",
    dependencies=[Guard],
)
async def get_exportar_tps(
    materia_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> StreamingResponse:
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    csv_content = await service.exportar_tps_csv(materia_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=tps_sin_corregir_{materia_id}.csv"},
    )


@router.get(
    "/monitor",
    response_model=MonitorResponse,
    dependencies=[Guard],
)
async def get_monitor(
    materia_id: UUID | None = Query(None),
    busqueda: str | None = Query(None),
    regional: str | None = Query(None),
    comision: str | None = Query(None),
    actividad: str | None = Query(None),
    min_actividad_cumplida: int | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> MonitorResponse:
    service = AnalisisService(db, current_user.tenant_id, current_user.user_id)
    filtros = {
        "materia_id": materia_id,
        "busqueda": busqueda,
        "regional": regional,
        "comision": comision,
        "actividad": actividad,
        "min_actividad_cumplida": min_actividad_cumplida,
    }
    filtros = {k: v for k, v in filtros.items() if v is not None}
    try:
        result = await service.get_monitor(filtros, current_user.roles, page, per_page)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return MonitorResponse(
        items=[MonitorItem(**item) for item in result.get("data", [])],
        total=result.get("total", 0),
    )
