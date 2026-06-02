"""Router para estructura académica: carreras, cohortes, materias."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_current_user, get_db, require_permission
from app.models.permisos import ESTRUCTURA_GESTIONAR
from app.schemas.estructura_academica import (
    CarreraCreate,
    CarreraResponse,
    CarreraUpdate,
    CohorteCreate,
    CohorteResponse,
    MateriaCreate,
    MateriaResponse,
    MateriaUpdate,
)
from app.services.auth import CurrentUser
from app.services.estructura_academica import (
    DuplicateError,
    EstructuraAcademicaService,
    InactiveCarreraError,
    NotFoundError,
)

router = APIRouter(prefix="/api/admin", tags=["estructura-academica"])

EstructuraGuard = Depends(require_permission(ESTRUCTURA_GESTIONAR))


# ── Carreras ────────────────────────────────────────────────────


@router.post("/carreras", response_model=CarreraResponse, status_code=status.HTTP_201_CREATED)
async def create_carrera(
    body: CarreraCreate,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> CarreraResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        carrera = await service.create_carrera(codigo=body.codigo, nombre=body.nombre)
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return CarreraResponse.model_validate(carrera)


@router.get("/carreras", response_model=list[CarreraResponse])
async def list_carreras(
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[CarreraResponse]:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    carreras = await service.list_carreras()
    return [CarreraResponse.model_validate(c) for c in carreras]


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
) -> CarreraResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        carrera = await service.update_carrera(carrera_id, nombre=body.nombre, estado=body.estado)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return CarreraResponse.model_validate(carrera)


@router.delete("/carreras/{carrera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carrera(
    carrera_id: UUID,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    deleted = await service.delete_carrera(carrera_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrera not found")


# ── Cohortes ────────────────────────────────────────────────────


@router.post("/cohortes", response_model=CohorteResponse, status_code=status.HTTP_201_CREATED)
async def create_cohorte(
    body: CohorteCreate,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> CohorteResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        cohorte = await service.create_cohorte(
            carrera_id=body.carrera_id,
            nombre=body.nombre,
            anio=body.anio,
            vig_desde=body.vig_desde,
            vig_hasta=body.vig_hasta,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (DuplicateError, InactiveCarreraError) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return CohorteResponse.model_validate(cohorte)


@router.get("/cohortes", response_model=list[CohorteResponse])
async def list_cohortes(
    carrera_id: UUID | None = Query(default=None),
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[CohorteResponse]:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    cohortes = await service.list_cohortes(carrera_id=carrera_id)
    return [CohorteResponse.model_validate(c) for c in cohortes]


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
) -> None:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    deleted = await service.delete_cohorte(cohorte_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cohorte not found")


# ── Materias ────────────────────────────────────────────────────


@router.post("/materias", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_materia(
    body: MateriaCreate,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> MateriaResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        materia = await service.create_materia(codigo=body.codigo, nombre=body.nombre)
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return MateriaResponse.model_validate(materia)


@router.get("/materias", response_model=list[MateriaResponse])
async def list_materias(
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[MateriaResponse]:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    materias = await service.list_materias()
    return [MateriaResponse.model_validate(m) for m in materias]


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
) -> MateriaResponse:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    try:
        materia = await service.update_materia(materia_id, nombre=body.nombre, estado=body.estado)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return MateriaResponse.model_validate(materia)


@router.delete("/materias/{materia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia(
    materia_id: UUID,
    _: CurrentUser = EstructuraGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    service = EstructuraAcademicaService(db, current_user.tenant_id)
    deleted = await service.delete_materia(materia_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Materia not found")
