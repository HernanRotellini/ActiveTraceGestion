"""Router para períodos académicos (setup de cuatrimestre)."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import PERIODOS_GESTIONAR
from app.schemas.periodos_academicos import (
    PeriodoAcademicoCreate,
    PeriodoAcademicoResponse,
    PeriodoAcademicoUpdate,
    PeriodoFechaCreate,
    PeriodoProgramaCreate,
    PeriodoFechaItem,
    PeriodoProgramaItem,
    PeriodosListResponse,
)
from app.services.auth import CurrentUser
from app.services.periodos_academicos import (
    InvalidPeriodoDatesError,
    NotFoundError,
    PeriodoAcademicoService,
)

router = APIRouter(prefix="/api/periodos-academicos", tags=["periodos-academicos"])

PeriodosGuard = Depends(require_permission(PERIODOS_GESTIONAR))


def _build_response(
    periodo,
    fechas: list,
    programas: list,
    materia_map: dict[UUID, str] | None = None,
) -> PeriodoAcademicoResponse:
    """Construye la respuesta con fechas y programas anidados."""
    return PeriodoAcademicoResponse(
        id=periodo.id,
        nombre=periodo.nombre,
        fecha_inicio=periodo.fecha_inicio,
        fecha_fin=periodo.fecha_fin,
        activo=periodo.activo,
        fechas=[
            PeriodoFechaItem(
                id=f.id,
                periodo_id=f.periodo_id,
                key=f.key,
                label=f.label,
                fecha=f.fecha,
            )
            for f in fechas
        ],
        programas=[
            PeriodoProgramaItem(
                id=p.id,
                periodo_id=p.periodo_id,
                materia_id=p.materia_id,
                materia_nombre=materia_map.get(p.materia_id, "Desconocida") if materia_map else str(p.materia_id),
                carrera=p.carrera,
                anio=p.anio,
                activo=p.activo,
            )
            for p in programas
        ],
    )


# ── Periodo CRUD ────────────────────────────────────────────────


@router.get("", response_model=PeriodosListResponse)
async def list_periodos(
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodosListResponse:
    """Lista todos los períodos académicos con fechas y programas."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    periodos = await service.list_all()

    from app.models.estructura_academica import Materia
    from sqlalchemy import select

    # Build materia map for names
    result = await db.execute(
        select(Materia).where(
            Materia.tenant_id == current_user.tenant_id,
            Materia.deleted_at.is_(None),
        )
    )
    materias = {m.id: m for m in list(result.scalars().all())}

    items = []
    for p in periodos:
        fechas = await service.list_fechas(p.id)
        programas = await service.list_programas(p.id)
        items.append(_build_response(p, fechas, programas, materias))

    return PeriodosListResponse(items=items)


@router.get("/{periodo_id}", response_model=PeriodoAcademicoResponse)
async def get_periodo(
    periodo_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodoAcademicoResponse:
    """Obtiene un período académico con sus fechas y programas."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    periodo = await service.get(periodo_id)
    if periodo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")

    from app.models.estructura_academica import Materia
    from sqlalchemy import select

    fechas = await service.list_fechas(periodo_id)
    programas = await service.list_programas(periodo_id)

    # Get materia names
    materia_ids = [p.materia_id for p in programas]
    if materia_ids:
        result = await db.execute(
            select(Materia).where(Materia.id.in_(materia_ids), Materia.deleted_at.is_(None))
        )
        materias = {m.id: m.nombre for m in list(result.scalars().all())}
    else:
        materias = {}

    return _build_response(periodo, fechas, programas, materias)


@router.post("", response_model=PeriodoAcademicoResponse, status_code=status.HTTP_201_CREATED)
async def create_periodo(
    body: PeriodoAcademicoCreate,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodoAcademicoResponse:
    """Crea un nuevo período académico."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    try:
        periodo = await service.create(
            nombre=body.nombre,
            fecha_inicio=body.fecha_inicio,
            fecha_fin=body.fecha_fin,
        )
    except InvalidPeriodoDatesError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _build_response(periodo, [], [], {})


@router.patch("/{periodo_id}", response_model=PeriodoAcademicoResponse)
async def update_periodo(
    periodo_id: UUID,
    body: PeriodoAcademicoUpdate,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodoAcademicoResponse:
    """Actualiza un período académico."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    try:
        periodo = await service.update(
            periodo_id,
            nombre=body.nombre,
            fecha_inicio=body.fecha_inicio,
            fecha_fin=body.fecha_fin,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidPeriodoDatesError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    fechas = await service.list_fechas(periodo_id)
    programas = await service.list_programas(periodo_id)
    return _build_response(periodo, fechas, programas)


@router.delete("/{periodo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_periodo(
    periodo_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    """Elimina (soft-delete) un período académico."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    deleted = await service.delete(periodo_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Periodo no encontrado")


# ── Activar / Desactivar ─────────────────────────────────────────


@router.post("/{periodo_id}/activar", response_model=PeriodoAcademicoResponse)
async def activar_periodo(
    periodo_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodoAcademicoResponse:
    """Activa un período (desactiva cualquier otro)."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    try:
        periodo = await service.activar(periodo_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    fechas = await service.list_fechas(periodo_id)
    programas = await service.list_programas(periodo_id)
    return _build_response(periodo, fechas, programas)


@router.post("/{periodo_id}/desactivar", response_model=PeriodoAcademicoResponse)
async def desactivar_periodo(
    periodo_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodoAcademicoResponse:
    """Desactiva un período."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    try:
        periodo = await service.desactivar(periodo_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    fechas = await service.list_fechas(periodo_id)
    programas = await service.list_programas(periodo_id)
    return _build_response(periodo, fechas, programas)


# ── Fechas ───────────────────────────────────────────────────────


@router.post("/{periodo_id}/fechas", response_model=PeriodoFechaItem, status_code=status.HTTP_201_CREATED)
async def add_fecha(
    periodo_id: UUID,
    body: PeriodoFechaCreate,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodoFechaItem:
    """Agrega una fecha académica al período."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    fecha = await service.add_fecha(
        periodo_id=periodo_id,
        key=body.key,
        label=body.label,
        fecha=body.fecha,
    )
    return PeriodoFechaItem(
        id=fecha.id,
        periodo_id=fecha.periodo_id,
        key=fecha.key,
        label=fecha.label,
        fecha=fecha.fecha,
    )


@router.delete("/{periodo_id}/fechas/{fecha_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_fecha(
    periodo_id: UUID,
    fecha_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    """Quita una fecha académica del período."""
    from app.services.periodos_academicos import PeriodoAcademicoService

    service = PeriodoAcademicoService(db, current_user.tenant_id)
    deleted = await service.remove_fecha(fecha_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fecha no encontrada")


# ── Programas ────────────────────────────────────────────────────


@router.post("/{periodo_id}/programas", response_model=PeriodoProgramaItem, status_code=status.HTTP_201_CREATED)
async def add_programa(
    periodo_id: UUID,
    body: PeriodoProgramaCreate,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodoProgramaItem:
    """Agrega un programa (materia) al período."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    programa = await service.add_programa(
        periodo_id=periodo_id,
        materia_id=body.materia_id,
        carrera=body.carrera,
        anio=body.anio,
    )

    from app.models.estructura_academica import Materia
    from sqlalchemy import select

    result = await db.execute(
        select(Materia).where(Materia.id == body.materia_id, Materia.deleted_at.is_(None))
    )
    materia = result.scalar_one_or_none()
    materia_nombre = materia.nombre if materia else str(body.materia_id)

    return PeriodoProgramaItem(
        id=programa.id,
        periodo_id=programa.periodo_id,
        materia_id=programa.materia_id,
        materia_nombre=materia_nombre,
        carrera=programa.carrera,
        anio=programa.anio,
        activo=programa.activo,
    )


@router.delete("/{periodo_id}/programas/{programa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_programa(
    periodo_id: UUID,
    programa_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    """Quita un programa del período."""
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    deleted = await service.remove_programa(programa_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programa no encontrado")
