"""Router para el módulo de evaluaciones y coloquios."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import COLOQUIOS_GESTIONAR, COLOQUIOS_RESERVAR
from app.schemas.coloquio import (
    AgendaResponse,
    AgendaReservaResponse,
    EvaluacionCreate,
    EvaluacionListResponse,
    EvaluacionResponse,
    ImportarAlumnosRequest,
    ImportarAlumnosResponse,
    MensajeResponse,
    MetricasResponse,
    ResultadoCreate,
    ResultadoResponse,
    ResultadosConsolidadosResponse,
    ReservaResponse,
    TurnoResponse,
)
from app.services.auth import CurrentUser
from app.services.coloquio_service import ColoquioError, ColoquioService

router = APIRouter(prefix="/api/coloquios", tags=["coloquios"])

GestionarGuard = Depends(require_permission(COLOQUIOS_GESTIONAR))
ReservarGuard = Depends(require_permission(COLOQUIOS_RESERVAR))


@router.get("/metricas", response_model=MetricasResponse)
async def panel_metricas(
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> MetricasResponse:
    """Panel de métricas global de coloquios (F7.1)."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    result = await service.metricas_globales()
    return MetricasResponse(**result)


@router.post("", response_model=EvaluacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_convocatoria(
    body: EvaluacionCreate,
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> EvaluacionResponse:
    """Crea una convocatoria de coloquio con turnos (F7.3)."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.crear_convocatoria(
            materia_id=body.materia_id,
            cohorte_id=body.cohorte_id,
            tipo=body.tipo,
            instancia=body.instancia,
            turnos_data=[t.model_dump() for t in body.turnos],
        )
    except ColoquioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return EvaluacionResponse(**result, turnos=[TurnoResponse(**t) for t in result["turnos"]])


@router.get("", response_model=list[EvaluacionListResponse])
async def listar_convocatorias(
    materia_id: UUID | None = None,
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[EvaluacionListResponse]:
    """Lista convocatorias con métricas (F7.4)."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    result = await service.listar_con_metricas(materia_id)
    return [EvaluacionListResponse(**item) for item in result]


@router.get("/{evaluacion_id}", response_model=EvaluacionResponse)
async def detalle_convocatoria(
    evaluacion_id: UUID,
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> EvaluacionResponse:
    """Detalle de una convocatoria con sus turnos."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    result = await service.detalle_convocatoria(evaluacion_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convocatoria no encontrada")
    return EvaluacionResponse(**result, turnos=[TurnoResponse(**t) for t in result["turnos"]])


@router.post("/{evaluacion_id}/importar-alumnos", response_model=ImportarAlumnosResponse)
async def importar_alumnos(
    evaluacion_id: UUID,
    body: ImportarAlumnosRequest,
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ImportarAlumnosResponse:
    """Importa alumnos a una convocatoria (F7.2)."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.importar_alumnos(evaluacion_id, body.alumno_ids)
    except ColoquioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ImportarAlumnosResponse(**result)


@router.get("/{evaluacion_id}/turnos", response_model=list[TurnoResponse])
async def listar_turnos(
    evaluacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[TurnoResponse]:
    """Lista turnos de una convocatoria con disponibilidad."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    result = await service.listar_turnos(evaluacion_id)
    return [TurnoResponse(**t) for t in result]


@router.post("/{evaluacion_id}/reservar", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
async def reservar_turno(
    evaluacion_id: UUID,
    turno_id: UUID,
    _: CurrentUser = ReservarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ReservaResponse:
    """ALUMNO reserva un turno en una convocatoria."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.reservar(evaluacion_id, turno_id)
    except ColoquioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ReservaResponse(**result)


@router.post("/{evaluacion_id}/cancelar-reserva", response_model=MensajeResponse)
async def cancelar_reserva(
    evaluacion_id: UUID,
    _: CurrentUser = ReservarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> MensajeResponse:
    """ALUMNO cancela su reserva activa en una convocatoria."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.cancelar_reserva(evaluacion_id)
    except ColoquioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return MensajeResponse(mensaje=result["mensaje"])


@router.get("/{evaluacion_id}/reservas", response_model=list[ReservaResponse])
async def listar_reservas(
    evaluacion_id: UUID,
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[ReservaResponse]:
    """Lista reservas de una convocatoria (gestión)."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    result = await service.listar_reservas(evaluacion_id)
    return [ReservaResponse(**r) for r in result]


@router.post("/{evaluacion_id}/resultados", response_model=ResultadoResponse)
async def registrar_resultado(
    evaluacion_id: UUID,
    body: ResultadoCreate,
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ResultadoResponse:
    """Registra o actualiza un resultado de evaluación."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.registrar_resultado(
            evaluacion_id, body.alumno_id, body.nota_final,
        )
    except ColoquioError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ResultadoResponse(**result)


@router.get("/{evaluacion_id}/resultados", response_model=list[ResultadoResponse])
async def consultar_resultados(
    evaluacion_id: UUID,
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[ResultadoResponse]:
    """Resultados consolidados de una convocatoria."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    result = await service.listar_resultados(evaluacion_id)
    return [ResultadoResponse(**r) for r in result]


@router.delete("/{evaluacion_id}", response_model=MensajeResponse)
async def cerrar_convocatoria(
    evaluacion_id: UUID,
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> MensajeResponse:
    """Cierra/elimina una convocatoria."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.cerrar_convocatoria(evaluacion_id)
    except ColoquioError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return MensajeResponse(mensaje=result["mensaje"])


@router.get("/admin/agenda", response_model=AgendaResponse)
async def agenda_global(
    _: CurrentUser = GestionarGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AgendaResponse:
    """Agenda consolidada de reservas activas (admin global)."""
    service = ColoquioService(db, current_user.tenant_id, current_user.user_id)
    items = await service.agenda_reservas()
    return AgendaResponse(
        items=[AgendaReservaResponse(**item) for item in items],
        total=len(items),
    )
