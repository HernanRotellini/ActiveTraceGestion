"""Router para tareas internas."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import TAREAS_GESTIONAR
from app.models.tarea import EstadoTarea
from app.schemas.tarea import (
    ComentarioTareaCreate,
    ComentarioTareaResponse,
    TareaCreate,
    TareaDelegate,
    TareaDetailResponse,
    TareaResponse,
    TareaStatusUpdate,
)
from app.services.auth import CurrentUser
from app.services.tarea_service import (
    TareaInvalidTransitionError,
    TareaNotFoundError,
    TareaService,
    TareaValidationError,
)

router = APIRouter(prefix="/api/tareas", tags=["tareas"])

TareasGuard = Depends(require_permission(TAREAS_GESTIONAR))


def _service(db: AsyncSession, current_user: CurrentUser) -> TareaService:
    return TareaService(db, current_user.tenant_id)


@router.post("", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
async def crear_tarea(
    body: TareaCreate,
    _: CurrentUser = TareasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> TareaResponse:
    try:
        tarea = await _service(db, current_user).create_task(
            actor_id=current_user.user_id,
            titulo=body.titulo,
            descripcion=body.descripcion,
            asignado_a=body.asignado_a,
            materia_id=body.materia_id,
            contexto_id=body.contexto_id,
        )
    except TareaValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TareaResponse.model_validate(tarea)


@router.get("/mis", response_model=list[TareaResponse])
async def listar_mis_tareas(
    _: CurrentUser = TareasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[TareaResponse]:
    tareas = await _service(db, current_user).list_my(current_user.user_id, limit=limit, offset=offset)
    return [TareaResponse.model_validate(tarea) for tarea in tareas]


@router.get("", response_model=list[TareaResponse])
async def listar_tareas(
    _: CurrentUser = TareasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    asignado_a: UUID | None = None,
    asignado_por: UUID | None = None,
    materia_id: UUID | None = None,
    estado: EstadoTarea | None = None,
    search: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[TareaResponse]:
    tareas = await _service(db, current_user).list_global(
        asignado_a=asignado_a,
        asignado_por=asignado_por,
        materia_id=materia_id,
        estado=estado,
        search=search,
        limit=limit,
        offset=offset,
    )
    return [TareaResponse.model_validate(tarea) for tarea in tareas]


@router.get("/{tarea_id}", response_model=TareaDetailResponse)
async def detalle_tarea(
    tarea_id: UUID,
    _: CurrentUser = TareasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> TareaDetailResponse:
    try:
        tarea = await _service(db, current_user).get_detail(tarea_id)
    except TareaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TareaDetailResponse.model_validate(tarea)


@router.post("/{tarea_id}/delegar", response_model=TareaResponse)
async def delegar_tarea(
    tarea_id: UUID,
    body: TareaDelegate,
    _: CurrentUser = TareasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> TareaResponse:
    try:
        tarea = await _service(db, current_user).delegate_task(
            tarea_id,
            actor_id=current_user.user_id,
            asignado_a=body.asignado_a,
        )
    except TareaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TareaValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TareaResponse.model_validate(tarea)


@router.patch("/{tarea_id}/estado", response_model=TareaResponse)
async def cambiar_estado_tarea(
    tarea_id: UUID,
    body: TareaStatusUpdate,
    _: CurrentUser = TareasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> TareaResponse:
    try:
        tarea = await _service(db, current_user).change_status(
            tarea_id,
            body.estado,
            actor_id=current_user.user_id,
        )
    except TareaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TareaInvalidTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TareaResponse.model_validate(tarea)


@router.post("/{tarea_id}/comentarios", response_model=ComentarioTareaResponse, status_code=status.HTTP_201_CREATED)
async def agregar_comentario(
    tarea_id: UUID,
    body: ComentarioTareaCreate,
    _: CurrentUser = TareasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> ComentarioTareaResponse:
    try:
        comentario = await _service(db, current_user).add_comment(
            tarea_id,
            autor_id=current_user.user_id,
            texto=body.texto,
        )
    except TareaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TareaValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ComentarioTareaResponse.model_validate(comentario)
