"""Router para periodos academicos del setup de cuatrimestre."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_audit_service, get_db, require_permission
from app.models.estructura_academica import Materia
from app.models.permisos import (
    ESTRUCTURA_GESTIONAR,
    PERIODO_ACTIVAR,
    PERIODO_CREAR,
    PERIODO_DESACTIVAR,
    PERIODO_EDITAR,
    PERIODO_ELIMINAR,
    PERIODO_FECHA_CREAR,
    PERIODO_FECHA_ELIMINAR,
    PERIODO_PROGRAMA_CREAR,
    PERIODO_PROGRAMA_ELIMINAR,
)
from app.schemas.periodos_academicos import (
    PeriodoAcademicoCreate,
    PeriodoAcademicoResponse,
    PeriodoAcademicoUpdate,
    PeriodoFechaCreate,
    PeriodoFechaItem,
    PeriodoProgramaCreate,
    PeriodoProgramaItem,
    PeriodosListResponse,
)
from app.services.audit import AuditService
from app.services.auth import CurrentUser
from app.services.periodos_academicos import (
    InvalidPeriodoDatesError,
    NotFoundError,
    PeriodoAcademicoService,
)

router = APIRouter(prefix="/api/periodos-academicos", tags=["periodos-academicos"])

PeriodosGuard = Depends(require_permission(ESTRUCTURA_GESTIONAR))


def periodo_audit_detail(periodo) -> dict[str, object]:
    return {
        "periodo_id": str(periodo.id),
        "nombre": periodo.nombre,
        "fecha_inicio": periodo.fecha_inicio.isoformat(),
        "fecha_fin": periodo.fecha_fin.isoformat(),
        "activo": periodo.activo,
    }


def periodo_fecha_audit_detail(fecha) -> dict[str, object]:
    return {
        "fecha_id": str(fecha.id),
        "periodo_id": str(fecha.periodo_id),
        "key": fecha.key,
        "label": fecha.label,
        "fecha": fecha.fecha.isoformat(),
    }


def periodo_programa_audit_detail(
    programa, materia_nombre: str | None = None
) -> dict[str, object]:
    return {
        "programa_id": str(programa.id),
        "periodo_id": str(programa.periodo_id),
        "materia_id": str(programa.materia_id),
        "materia_nombre": materia_nombre,
        "carrera": programa.carrera,
        "anio": programa.anio,
        "activo": programa.activo,
    }


def _build_response(
    periodo,
    fechas: list,
    programas: list,
    materia_map: dict[UUID, str] | None = None,
) -> PeriodoAcademicoResponse:
    return PeriodoAcademicoResponse(
        id=periodo.id,
        nombre=periodo.nombre,
        fecha_inicio=periodo.fecha_inicio,
        fecha_fin=periodo.fecha_fin,
        activo=periodo.activo,
        fechas=[
            PeriodoFechaItem(
                id=fecha.id,
                periodo_id=fecha.periodo_id,
                key=fecha.key,
                label=fecha.label,
                fecha=fecha.fecha,
            )
            for fecha in fechas
        ],
        programas=[
            PeriodoProgramaItem(
                id=programa.id,
                periodo_id=programa.periodo_id,
                materia_id=programa.materia_id,
                materia_nombre=(
                    materia_map.get(programa.materia_id, "Desconocida")
                    if materia_map
                    else str(programa.materia_id)
                ),
                carrera=programa.carrera,
                anio=programa.anio,
                activo=programa.activo,
            )
            for programa in programas
        ],
    )


async def _materia_name_map(
    db: AsyncSession, tenant_id: UUID, materia_ids: list[UUID] | None = None
) -> dict[UUID, str]:
    query = select(Materia).where(
        Materia.tenant_id == tenant_id,
        Materia.deleted_at.is_(None),
    )
    if materia_ids:
        query = query.where(Materia.id.in_(materia_ids))

    result = await db.execute(query)
    return {materia.id: materia.nombre for materia in list(result.scalars().all())}


@router.get("", response_model=PeriodosListResponse)
async def list_periodos(
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodosListResponse:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    periodos = await service.list_all()
    materias = await _materia_name_map(db, current_user.tenant_id)

    items = []
    for periodo in periodos:
        fechas = await service.list_fechas(periodo.id)
        programas = await service.list_programas(periodo.id)
        items.append(_build_response(periodo, fechas, programas, materias))

    return PeriodosListResponse(items=items)


@router.get("/{periodo_id}", response_model=PeriodoAcademicoResponse)
async def get_periodo(
    periodo_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PeriodoAcademicoResponse:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    periodo = await service.get(periodo_id)
    if periodo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Periodo no encontrado",
        )

    fechas = await service.list_fechas(periodo_id)
    programas = await service.list_programas(periodo_id)
    materia_ids = [programa.materia_id for programa in programas]
    materias = await _materia_name_map(db, current_user.tenant_id, materia_ids)

    return _build_response(periodo, fechas, programas, materias)


@router.post("", response_model=PeriodoAcademicoResponse, status_code=status.HTTP_201_CREATED)
async def create_periodo(
    body: PeriodoAcademicoCreate,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> PeriodoAcademicoResponse:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    try:
        periodo = await service.create(
            nombre=body.nombre,
            fecha_inicio=body.fecha_inicio,
            fecha_fin=body.fecha_fin,
        )
    except InvalidPeriodoDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    await audit.log(
        accion=PERIODO_CREAR,
        detalle=periodo_audit_detail(periodo),
        filas_afectadas=1,
    )
    return _build_response(periodo, [], [], {})


@router.patch("/{periodo_id}", response_model=PeriodoAcademicoResponse)
async def update_periodo(
    periodo_id: UUID,
    body: PeriodoAcademicoUpdate,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> PeriodoAcademicoResponse:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    current = await service.get(periodo_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PeriodoAcademico with id '{periodo_id}' not found",
        )

    nombre_anterior = current.nombre
    fecha_inicio_anterior = current.fecha_inicio
    fecha_fin_anterior = current.fecha_fin

    try:
        periodo = await service.update(
            periodo_id,
            nombre=body.nombre,
            fecha_inicio=body.fecha_inicio,
            fecha_fin=body.fecha_fin,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InvalidPeriodoDatesError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    cambios: dict[str, dict[str, object]] = {}
    if body.nombre is not None and body.nombre != nombre_anterior:
        cambios["nombre"] = {"anterior": nombre_anterior, "nuevo": periodo.nombre}
    if body.fecha_inicio is not None and body.fecha_inicio != fecha_inicio_anterior:
        cambios["fecha_inicio"] = {
            "anterior": fecha_inicio_anterior.isoformat(),
            "nuevo": periodo.fecha_inicio.isoformat(),
        }
    if body.fecha_fin is not None and body.fecha_fin != fecha_fin_anterior:
        cambios["fecha_fin"] = {
            "anterior": fecha_fin_anterior.isoformat(),
            "nuevo": periodo.fecha_fin.isoformat(),
        }

    if cambios:
        await audit.log(
            accion=PERIODO_EDITAR,
            detalle={**periodo_audit_detail(periodo), "cambios": cambios},
            filas_afectadas=1,
        )

    fechas = await service.list_fechas(periodo_id)
    programas = await service.list_programas(periodo_id)
    materias = await _materia_name_map(
        db, current_user.tenant_id, [programa.materia_id for programa in programas]
    )
    return _build_response(periodo, fechas, programas, materias)


@router.delete("/{periodo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_periodo(
    periodo_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> None:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    periodo = await service.get(periodo_id)
    deleted = await service.delete(periodo_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Periodo no encontrado",
        )

    if periodo is not None:
        await audit.log(
            accion=PERIODO_ELIMINAR,
            detalle=periodo_audit_detail(periodo),
            filas_afectadas=1,
        )


@router.post("/{periodo_id}/activar", response_model=PeriodoAcademicoResponse)
async def activar_periodo(
    periodo_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> PeriodoAcademicoResponse:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    current = await service.get(periodo_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PeriodoAcademico with id '{periodo_id}' not found",
        )

    otros_activos = [
        str(periodo.id)
        for periodo in await service.list_all()
        if periodo.id != periodo_id and periodo.activo
    ]

    try:
        periodo = await service.activar(periodo_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    await audit.log(
        accion=PERIODO_ACTIVAR,
        detalle={
            **periodo_audit_detail(periodo),
            "estado_anterior": current.activo,
            "estado_nuevo": periodo.activo,
            "periodos_desactivados": otros_activos,
        },
        filas_afectadas=1 + len(otros_activos),
    )

    fechas = await service.list_fechas(periodo_id)
    programas = await service.list_programas(periodo_id)
    materias = await _materia_name_map(
        db, current_user.tenant_id, [programa.materia_id for programa in programas]
    )
    return _build_response(periodo, fechas, programas, materias)


@router.post("/{periodo_id}/desactivar", response_model=PeriodoAcademicoResponse)
async def desactivar_periodo(
    periodo_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> PeriodoAcademicoResponse:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    current = await service.get(periodo_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PeriodoAcademico with id '{periodo_id}' not found",
        )

    try:
        periodo = await service.desactivar(periodo_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if current.activo != periodo.activo:
        await audit.log(
            accion=PERIODO_DESACTIVAR,
            detalle={
                **periodo_audit_detail(periodo),
                "estado_anterior": current.activo,
                "estado_nuevo": periodo.activo,
            },
            filas_afectadas=1,
        )

    fechas = await service.list_fechas(periodo_id)
    programas = await service.list_programas(periodo_id)
    materias = await _materia_name_map(
        db, current_user.tenant_id, [programa.materia_id for programa in programas]
    )
    return _build_response(periodo, fechas, programas, materias)


@router.post(
    "/{periodo_id}/fechas",
    response_model=PeriodoFechaItem,
    status_code=status.HTTP_201_CREATED,
)
async def add_fecha(
    periodo_id: UUID,
    body: PeriodoFechaCreate,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> PeriodoFechaItem:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    fecha = await service.add_fecha(
        periodo_id=periodo_id,
        key=body.key,
        label=body.label,
        fecha=body.fecha,
    )
    await audit.log(
        accion=PERIODO_FECHA_CREAR,
        detalle=periodo_fecha_audit_detail(fecha),
        filas_afectadas=1,
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
    audit: AuditService = Depends(get_audit_service),
) -> None:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    fecha = next(
        (item for item in await service.list_fechas(periodo_id) if item.id == fecha_id),
        None,
    )
    deleted = await service.remove_fecha(fecha_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fecha no encontrada",
        )

    if fecha is not None:
        await audit.log(
            accion=PERIODO_FECHA_ELIMINAR,
            detalle=periodo_fecha_audit_detail(fecha),
            filas_afectadas=1,
        )


@router.post(
    "/{periodo_id}/programas",
    response_model=PeriodoProgramaItem,
    status_code=status.HTTP_201_CREATED,
)
async def add_programa(
    periodo_id: UUID,
    body: PeriodoProgramaCreate,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> PeriodoProgramaItem:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    programa = await service.add_programa(
        periodo_id=periodo_id,
        materia_id=body.materia_id,
        carrera=body.carrera,
        anio=body.anio,
    )

    result = await db.execute(
        select(Materia).where(
            Materia.id == body.materia_id,
            Materia.deleted_at.is_(None),
        )
    )
    materia = result.scalar_one_or_none()
    materia_nombre = materia.nombre if materia else str(body.materia_id)

    await audit.log(
        accion=PERIODO_PROGRAMA_CREAR,
        detalle=periodo_programa_audit_detail(programa, materia_nombre),
        filas_afectadas=1,
    )

    return PeriodoProgramaItem(
        id=programa.id,
        periodo_id=programa.periodo_id,
        materia_id=programa.materia_id,
        materia_nombre=materia_nombre,
        carrera=programa.carrera,
        anio=programa.anio,
        activo=programa.activo,
    )


@router.delete(
    "/{periodo_id}/programas/{programa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_programa(
    periodo_id: UUID,
    programa_id: UUID,
    _: CurrentUser = PeriodosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> None:
    service = PeriodoAcademicoService(db, current_user.tenant_id)
    programa = next(
        (item for item in await service.list_programas(periodo_id) if item.id == programa_id),
        None,
    )
    deleted = await service.remove_programa(programa_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado",
        )

    if programa is not None:
        result = await db.execute(
            select(Materia).where(
                Materia.id == programa.materia_id,
                Materia.deleted_at.is_(None),
            )
        )
        materia = result.scalar_one_or_none()
        await audit.log(
            accion=PERIODO_PROGRAMA_ELIMINAR,
            detalle=periodo_programa_audit_detail(
                programa,
                materia.nombre if materia else None,
            ),
            filas_afectadas=1,
        )
