"""Routers para grilla salarial y liquidaciones."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import LIQUIDACIONES_CALCULAR_CERRAR, LIQUIDACIONES_OPERAR_GRILLA
from app.models.liquidaciones import SegmentoLiquidacion
from app.schemas.liquidaciones import (
    LiquidacionCloseRequest,
    LiquidacionPreviewRequest,
    LiquidacionPreviewResponse,
    LiquidacionResponse,
    MateriaPlusCreate,
    MateriaPlusResponse,
    SalarioBaseCreate,
    SalarioBaseResponse,
    SalarioBaseUpdate,
    SalarioPlusCreate,
    SalarioPlusResponse,
)
from app.services.auth import CurrentUser
from app.services.grilla_salarial_service import (
    GrillaSalarialContextError,
    GrillaSalarialNotFoundError,
    GrillaSalarialOverlapError,
    GrillaSalarialService,
    GrillaSalarialValidationError,
)
from app.services.liquidacion_service import (
    LiquidacionAlreadyClosedError,
    LiquidacionContextError,
    LiquidacionMissingConfigurationError,
    LiquidacionNotFoundError,
    LiquidacionService,
)

router = APIRouter(prefix="/api/liquidaciones", tags=["liquidaciones"])

GrillaGuard = Depends(require_permission(LIQUIDACIONES_OPERAR_GRILLA))
LiquidacionesGuard = Depends(require_permission(LIQUIDACIONES_CALCULAR_CERRAR))


def _grilla_service(db: AsyncSession, current_user: CurrentUser) -> GrillaSalarialService:
    return GrillaSalarialService(db, current_user.tenant_id)


def _liquidacion_service(db: AsyncSession, current_user: CurrentUser) -> LiquidacionService:
    return LiquidacionService(db, current_user.tenant_id)


def _map_grilla_error(exc: GrillaSalarialValidationError | GrillaSalarialOverlapError | GrillaSalarialContextError) -> HTTPException:
    if isinstance(exc, GrillaSalarialContextError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, GrillaSalarialOverlapError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/grilla/bases", response_model=SalarioBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_salario_base(
    body: SalarioBaseCreate,
    _: CurrentUser = GrillaGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> SalarioBaseResponse:
    try:
        record = await _grilla_service(db, current_user).create_salario_base(
            rol=body.rol, monto=body.monto, desde=body.desde, hasta=body.hasta
        )
    except (GrillaSalarialValidationError, GrillaSalarialOverlapError, GrillaSalarialContextError) as exc:
        raise _map_grilla_error(exc) from exc
    return SalarioBaseResponse.model_validate(record)


@router.get("/grilla/bases", response_model=list[SalarioBaseResponse])
async def list_salarios_base(
    _: CurrentUser = GrillaGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[SalarioBaseResponse]:
    records = await _grilla_service(db, current_user).list_salarios_base()
    return [SalarioBaseResponse.model_validate(record) for record in records]


@router.put("/grilla/bases/{salario_id}", response_model=SalarioBaseResponse)
async def update_salario_base(
    salario_id: UUID,
    body: SalarioBaseUpdate,
    _: CurrentUser = GrillaGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> SalarioBaseResponse:
    try:
        record = await _grilla_service(db, current_user).update_salario_base(
            salario_id, rol=body.rol, monto=body.monto, desde=body.desde, hasta=body.hasta
        )
    except GrillaSalarialNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (GrillaSalarialValidationError, GrillaSalarialOverlapError, GrillaSalarialContextError) as exc:
        raise _map_grilla_error(exc) from exc
    return SalarioBaseResponse.model_validate(record)


@router.delete("/grilla/bases/{salario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salario_base(
    salario_id: UUID,
    _: CurrentUser = GrillaGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    try:
        await _grilla_service(db, current_user).delete_salario_base(salario_id)
    except GrillaSalarialNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/grilla/pluses", response_model=SalarioPlusResponse, status_code=status.HTTP_201_CREATED)
async def create_salario_plus(
    body: SalarioPlusCreate,
    _: CurrentUser = GrillaGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> SalarioPlusResponse:
    try:
        record = await _grilla_service(db, current_user).create_salario_plus(
            rol=body.rol,
            grupo=body.grupo,
            descripcion=body.descripcion,
            monto=body.monto,
            desde=body.desde,
            hasta=body.hasta,
        )
    except (GrillaSalarialValidationError, GrillaSalarialOverlapError, GrillaSalarialContextError) as exc:
        raise _map_grilla_error(exc) from exc
    return SalarioPlusResponse.model_validate(record)


@router.get("/grilla/pluses", response_model=list[SalarioPlusResponse])
async def list_salarios_plus(
    _: CurrentUser = GrillaGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[SalarioPlusResponse]:
    records = await _grilla_service(db, current_user).list_salarios_plus()
    return [SalarioPlusResponse.model_validate(record) for record in records]


@router.post("/grilla/materia-plus", response_model=MateriaPlusResponse, status_code=status.HTTP_201_CREATED)
async def create_materia_plus(
    body: MateriaPlusCreate,
    _: CurrentUser = GrillaGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> MateriaPlusResponse:
    try:
        record = await _grilla_service(db, current_user).create_materia_plus(
            materia_id=body.materia_id, grupo=body.grupo, desde=body.desde, hasta=body.hasta
        )
    except (GrillaSalarialValidationError, GrillaSalarialOverlapError, GrillaSalarialContextError) as exc:
        raise _map_grilla_error(exc) from exc
    return MateriaPlusResponse.model_validate(record)


@router.get("/grilla/materia-plus", response_model=list[MateriaPlusResponse])
async def list_materia_plus(
    _: CurrentUser = GrillaGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[MateriaPlusResponse]:
    records = await _grilla_service(db, current_user).list_materia_plus()
    return [MateriaPlusResponse.model_validate(record) for record in records]


@router.post("/preview", response_model=LiquidacionPreviewResponse)
async def preview_liquidacion(
    body: LiquidacionPreviewRequest,
    _: CurrentUser = LiquidacionesGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> LiquidacionPreviewResponse:
    try:
        preview = await _liquidacion_service(db, current_user).preview(cohorte_id=body.cohorte_id, periodo=body.periodo)
    except LiquidacionContextError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LiquidacionMissingConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return LiquidacionPreviewResponse.model_validate(preview)


@router.post("/cerrar", response_model=list[LiquidacionResponse], status_code=status.HTTP_201_CREATED)
async def cerrar_liquidacion(
    body: LiquidacionCloseRequest,
    _: CurrentUser = LiquidacionesGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[LiquidacionResponse]:
    try:
        closed = await _liquidacion_service(db, current_user).close(
            cohorte_id=body.cohorte_id, periodo=body.periodo, actor_id=current_user.user_id
        )
    except LiquidacionContextError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LiquidacionAlreadyClosedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LiquidacionMissingConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return [LiquidacionResponse.model_validate(record) for record in closed]


@router.get("", response_model=list[LiquidacionResponse])
async def list_liquidaciones(
    _: CurrentUser = LiquidacionesGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    periodo: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    cohorte_id: UUID | None = Query(default=None),
    usuario_id: UUID | None = Query(default=None),
    segmento: SegmentoLiquidacion | None = Query(default=None),
) -> list[LiquidacionResponse]:
    records = await _liquidacion_service(db, current_user).list_closed(
        periodo=periodo, cohorte_id=cohorte_id, usuario_id=usuario_id, segmento=segmento
    )
    return [LiquidacionResponse.model_validate(record) for record in records]


@router.get("/{liquidacion_id}", response_model=LiquidacionResponse)
async def get_liquidacion(
    liquidacion_id: UUID,
    _: CurrentUser = LiquidacionesGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> LiquidacionResponse:
    try:
        record = await _liquidacion_service(db, current_user).get(liquidacion_id)
    except LiquidacionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return LiquidacionResponse.model_validate(record)
