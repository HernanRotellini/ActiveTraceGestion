"""Router para estructura académica: carreras, cohortes, materias."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_current_user, get_audit_service, get_db, require_permission
from app.models.permisos import (
    CARRERA_CAMBIAR_ESTADO,
    CARRERA_CREAR,
    CARRERA_EDITAR,
    CARRERA_ELIMINAR,
    COHORTE_CAMBIAR_ESTADO,
    COHORTE_CREAR,
    COHORTE_EDITAR,
    COHORTE_ELIMINAR,
    ESTRUCTURA_GESTIONAR,
    MATERIA_CAMBIAR_ESTADO,
    MATERIA_CREAR,
    MATERIA_EDITAR,
    MATERIA_ELIMINAR,
)
from app.schemas.estructura_academica import (
    CarreraCreate,
    CarreraResponse,
    CarreraUpdate,
    CohorteCreate,
    CohorteResponse,
    CohorteUpdate,
    MateriaCreate,
    MateriaResponse,
    MateriaUpdate,
    EstadoAcademico,
)
from app.services.auth import CurrentUser
from app.services.audit import AuditService
from app.services.estructura_academica import (
    DeleteBlockedError,
    DuplicateError,
    EstructuraAcademicaService,
    InactiveCarreraError,
    InactiveCohorteError,
    NotFoundError,
)

router = APIRouter(prefix="/api/admin", tags=["estructura-academica"])

EstructuraGuard = Depends(require_permission(ESTRUCTURA_GESTIONAR))


def wrap_list(items: list) -> dict:
    return {"items": items, "total": len(items)}


def carrera_audit_detail(carrera) -> dict[str, str]:
    return {
        "carrera_id": str(carrera.id),
        "codigo": carrera.codigo,
        "nombre": carrera.nombre,
        "estado": carrera.estado,
    }


def cohorte_audit_detail(cohorte) -> dict[str, object]:
    return {
        "cohorte_id": str(cohorte.id),
        "carrera_id": str(cohorte.carrera_id),
        "nombre": cohorte.nombre,
        "anio": cohorte.anio,
        "vig_desde": cohorte.vig_desde.isoformat(),
        "vig_hasta": cohorte.vig_hasta.isoformat() if cohorte.vig_hasta else None,
        "estado": cohorte.estado,
    }


def materia_audit_detail(materia) -> dict[str, object]:
    return {
        "materia_id": str(materia.id),
        "codigo": materia.codigo,
        "nombre": materia.nombre,
        "carrera_id": str(materia.carrera_id) if materia.carrera_id else None,
        "cohorte_id": str(materia.cohorte_id) if materia.cohorte_id else None,
        "carga_horaria": materia.carga_horaria,
        "estado": materia.estado,
    }


# ── Carreras ────────────────────────────────────────────────────


@router.post("/carreras", response_model=CarreraResponse, status_code=status.HTTP_201_CREATED)
async def create_carrera(
    body: CarreraCreate,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> CarreraResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        carrera = await service.create_carrera(
            codigo=body.codigo,
            nombre=body.nombre,
            descripcion=body.descripcion,
            estado=body.estado,
        )
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    response = CarreraResponse.model_validate(carrera)
    await audit.log(
        accion=CARRERA_CREAR,
        detalle=carrera_audit_detail(carrera),
        filas_afectadas=1,
    )
    return response


@router.get("/carreras")
async def list_carreras(
    codigo: str | None = Query(default=None),
    nombre: str | None = Query(default=None),
    estado: EstadoAcademico | None = Query(default=None),
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> dict:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    carreras = await service.list_carreras(codigo=codigo, nombre=nombre, estado=estado)
    return wrap_list([CarreraResponse.model_validate(c) for c in carreras])


@router.get("/carreras/{carrera_id}", response_model=CarreraResponse)
async def get_carrera(
    carrera_id: UUID,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> CarreraResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    carrera = await service.get_carrera(carrera_id)
    if carrera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrera not found")
    return CarreraResponse.model_validate(carrera)


@router.patch("/carreras/{carrera_id}", response_model=CarreraResponse)
async def update_carrera(
    carrera_id: UUID,
    body: CarreraUpdate,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> CarreraResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        current = await service.get_carrera(carrera_id)
        if current is None:
            raise NotFoundError(f"Carrera with id '{carrera_id}' not found")
        estado_anterior = current.estado
        codigo_anterior = current.codigo
        nombre_anterior = current.nombre
        descripcion_anterior = current.descripcion
        carrera = await service.update_carrera(carrera_id, nombre=body.nombre, codigo=body.codigo, descripcion=body.descripcion, estado=body.estado)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    response = CarreraResponse.model_validate(carrera)
    changed_fields: dict[str, dict[str, str]] = {}
    if body.codigo is not None and body.codigo != codigo_anterior:
        changed_fields["codigo"] = {"anterior": codigo_anterior, "nuevo": carrera.codigo}
    if body.nombre is not None and body.nombre != nombre_anterior:
        changed_fields["nombre"] = {"anterior": nombre_anterior, "nuevo": carrera.nombre}
    if body.descripcion is not None and body.descripcion != descripcion_anterior:
        changed_fields["descripcion"] = {"anterior": descripcion_anterior, "nuevo": carrera.descripcion}
    if changed_fields:
        await audit.log(
            accion=CARRERA_EDITAR,
            detalle={
                **carrera_audit_detail(carrera),
                "cambios": changed_fields,
            },
            filas_afectadas=1,
        )
    if body.estado is not None and body.estado != estado_anterior:
        await audit.log(
            accion=CARRERA_CAMBIAR_ESTADO,
            detalle={
                "carrera_id": str(carrera.id),
                "codigo": carrera.codigo,
                "nombre": carrera.nombre,
                "estado_anterior": estado_anterior,
                "estado_nuevo": carrera.estado,
            },
            filas_afectadas=1,
        )
    return response


@router.delete("/carreras/{carrera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carrera(
    carrera_id: UUID,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> None:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    carrera = await service.get_carrera(carrera_id)
    try:
        deleted = await service.delete_carrera(carrera_id)
    except DeleteBlockedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrera not found")
    if carrera is not None:
        await audit.log(
            accion=CARRERA_ELIMINAR,
            detalle=carrera_audit_detail(carrera),
            filas_afectadas=1,
        )


# ── Cohortes ────────────────────────────────────────────────────


@router.post("/cohortes", response_model=CohorteResponse, status_code=status.HTTP_201_CREATED)
async def create_cohorte(
    body: CohorteCreate,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> CohorteResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        cohorte = await service.create_cohorte(
            carrera_id=body.carrera_id,
            nombre=body.nombre,
            anio=body.anio,
            vig_desde=body.vig_desde,
            vig_hasta=body.vig_hasta,
            estado=body.estado,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (DuplicateError, InactiveCarreraError) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    response = CohorteResponse.model_validate(cohorte)
    await audit.log(
        accion=COHORTE_CREAR,
        detalle=cohorte_audit_detail(cohorte),
        filas_afectadas=1,
    )
    return response


@router.get("/cohortes")
async def list_cohortes(
    carrera_id: UUID | None = Query(default=None),
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> dict:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    cohortes = await service.list_cohortes(carrera_id=carrera_id)
    return wrap_list([CohorteResponse.model_validate(c) for c in cohortes])


@router.get("/cohortes/{cohorte_id}", response_model=CohorteResponse)
async def get_cohorte(
    cohorte_id: UUID,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> CohorteResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    cohorte = await service.get_cohorte(cohorte_id)
    if cohorte is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohorte not found")
    return CohorteResponse.model_validate(cohorte)


@router.delete("/cohortes/{cohorte_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cohorte(
    cohorte_id: UUID,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> None:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    cohorte = await service.get_cohorte(cohorte_id)
    deleted = await service.delete_cohorte(cohorte_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohorte not found")
    if cohorte is not None:
        await audit.log(
            accion=COHORTE_ELIMINAR,
            detalle=cohorte_audit_detail(cohorte),
            filas_afectadas=1,
        )


@router.patch("/cohortes/{cohorte_id}", response_model=CohorteResponse)
async def update_cohorte(
    cohorte_id: UUID,
    body: CohorteUpdate,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> CohorteResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        current = await service.get_cohorte(cohorte_id)
        if current is None:
            raise NotFoundError(f"Cohorte with id '{cohorte_id}' not found")
        estado_anterior = current.estado
        nombre_anterior = current.nombre
        anio_anterior = current.anio
        vig_desde_anterior = current.vig_desde
        vig_hasta_anterior = current.vig_hasta
        cohorte = await service.update_cohorte(
            cohorte_id,
            nombre=body.nombre,
            anio=body.anio,
            vig_desde=body.vig_desde,
            vig_hasta=body.vig_hasta,
            vig_hasta_set="vig_hasta" in body.model_fields_set,
            estado=body.estado,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    response = CohorteResponse.model_validate(cohorte)
    changed_fields: dict[str, dict[str, object]] = {}
    if body.nombre is not None and body.nombre != nombre_anterior:
        changed_fields["nombre"] = {"anterior": nombre_anterior, "nuevo": cohorte.nombre}
    if body.anio is not None and body.anio != anio_anterior:
        changed_fields["anio"] = {"anterior": anio_anterior, "nuevo": cohorte.anio}
    if body.vig_desde is not None and body.vig_desde != vig_desde_anterior:
        changed_fields["vig_desde"] = {
            "anterior": vig_desde_anterior.isoformat(),
            "nuevo": cohorte.vig_desde.isoformat(),
        }
    if "vig_hasta" in body.model_fields_set and body.vig_hasta != vig_hasta_anterior:
        changed_fields["vig_hasta"] = {
            "anterior": vig_hasta_anterior.isoformat() if vig_hasta_anterior else None,
            "nuevo": cohorte.vig_hasta.isoformat() if cohorte.vig_hasta else None,
        }
    if changed_fields:
        await audit.log(
            accion=COHORTE_EDITAR,
            detalle={
                **cohorte_audit_detail(cohorte),
                "cambios": changed_fields,
            },
            filas_afectadas=1,
        )
    if body.estado is not None and body.estado != estado_anterior:
        await audit.log(
            accion=COHORTE_CAMBIAR_ESTADO,
            detalle={
                **cohorte_audit_detail(cohorte),
                "estado_anterior": estado_anterior,
                "estado_nuevo": cohorte.estado,
            },
            filas_afectadas=1,
        )
    return response


# ── Materias ────────────────────────────────────────────────────


@router.post("/materias", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_materia(
    body: MateriaCreate,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> MateriaResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        materia = await service.create_materia(
            codigo=body.codigo,
            nombre=body.nombre,
            carrera_id=body.carrera_id,
            cohorte_id=body.cohorte_id,
            carga_horaria=body.carga_horaria,
            estado=body.estado,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except (InactiveCarreraError, InactiveCohorteError) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    response = MateriaResponse.model_validate(materia)
    await audit.log(
        accion=MATERIA_CREAR,
        detalle=materia_audit_detail(materia),
        filas_afectadas=1,
    )
    return response


@router.get("/materias")
async def list_materias(
    carrera_id: UUID | None = Query(default=None),
    cohorte_id: UUID | None = Query(default=None),
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> dict:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    materias = await service.list_materias(carrera_id=carrera_id, cohorte_id=cohorte_id)
    return wrap_list([MateriaResponse.model_validate(m) for m in materias])


@router.get("/materias/{materia_id}", response_model=MateriaResponse)
async def get_materia(
    materia_id: UUID,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> MateriaResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    materia = await service.get_materia(materia_id)
    if materia is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia not found")
    return MateriaResponse.model_validate(materia)


@router.patch("/materias/{materia_id}", response_model=MateriaResponse)
async def update_materia(
    materia_id: UUID,
    body: MateriaUpdate,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> MateriaResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        current = await service.get_materia(materia_id)
        if current is None:
            raise NotFoundError(f"Materia with id '{materia_id}' not found")
        estado_anterior = current.estado
        codigo_anterior = current.codigo
        nombre_anterior = current.nombre
        carrera_id_anterior = current.carrera_id
        cohorte_id_anterior = current.cohorte_id
        carga_horaria_anterior = current.carga_horaria
        materia = await service.update_materia(
            materia_id,
            nombre=body.nombre,
            codigo=body.codigo,
            carrera_id=body.carrera_id,
            cohorte_id=body.cohorte_id,
            carga_horaria=body.carga_horaria,
            estado=body.estado,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except (InactiveCarreraError, InactiveCohorteError) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    response = MateriaResponse.model_validate(materia)
    changed_fields: dict[str, dict[str, object]] = {}
    if body.codigo is not None and body.codigo != codigo_anterior:
        changed_fields["codigo"] = {"anterior": codigo_anterior, "nuevo": materia.codigo}
    if body.nombre is not None and body.nombre != nombre_anterior:
        changed_fields["nombre"] = {"anterior": nombre_anterior, "nuevo": materia.nombre}
    if body.carrera_id is not None and body.carrera_id != carrera_id_anterior:
        changed_fields["carrera_id"] = {
            "anterior": str(carrera_id_anterior) if carrera_id_anterior else None,
            "nuevo": str(materia.carrera_id) if materia.carrera_id else None,
        }
    if body.cohorte_id is not None and body.cohorte_id != cohorte_id_anterior:
        changed_fields["cohorte_id"] = {
            "anterior": str(cohorte_id_anterior) if cohorte_id_anterior else None,
            "nuevo": str(materia.cohorte_id) if materia.cohorte_id else None,
        }
    if body.carga_horaria is not None and body.carga_horaria != carga_horaria_anterior:
        changed_fields["carga_horaria"] = {"anterior": carga_horaria_anterior, "nuevo": materia.carga_horaria}
    if changed_fields:
        await audit.log(
            accion=MATERIA_EDITAR,
            detalle={
                **materia_audit_detail(materia),
                "cambios": changed_fields,
            },
            filas_afectadas=1,
        )
    if body.estado is not None and body.estado != estado_anterior:
        await audit.log(
            accion=MATERIA_CAMBIAR_ESTADO,
            detalle={
                **materia_audit_detail(materia),
                "estado_anterior": estado_anterior,
                "estado_nuevo": materia.estado,
            },
            filas_afectadas=1,
        )
    return response


@router.delete("/materias/{materia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia(
    materia_id: UUID,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    audit: AuditService = Depends(get_audit_service),
) -> None:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    materia = await service.get_materia(materia_id)
    deleted = await service.delete_materia(materia_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia not found")
    if materia is not None:
        await audit.log(
            accion=MATERIA_ELIMINAR,
            detalle=materia_audit_detail(materia),
            filas_afectadas=1,
        )
