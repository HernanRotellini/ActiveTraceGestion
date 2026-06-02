"""Router administrativo para catálogo RBAC."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.models.permisos import ESTRUCTURA_GESTIONAR
from app.repositories.rbac import PermisoRepository, RolPermisoRepository, RolRepository
from app.schemas.rbac import PermisoResponse, RolPermisoResponse, RolResponse
from app.services.auth import CurrentUser

router = APIRouter(prefix="/api/admin/rbac", tags=["rbac"])

CurrentUserDep = Depends(get_current_user)


@router.get("/roles", response_model=list[RolResponse])
async def list_roles(
    _: CurrentUser = Depends(require_permission(ESTRUCTURA_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[RolResponse]:
    repo = RolRepository(db, current_user.tenant_id)
    roles = await repo.list()
    return [RolResponse.model_validate(r) for r in roles]


@router.get("/permisos", response_model=list[PermisoResponse])
async def list_permisos(
    _: CurrentUser = Depends(require_permission(ESTRUCTURA_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[PermisoResponse]:
    repo = PermisoRepository(db, current_user.tenant_id)
    permisos = await repo.list()
    return [PermisoResponse.model_validate(p) for p in permisos]


@router.get("/asignaciones", response_model=list[RolPermisoResponse])
async def list_asignaciones(
    _: CurrentUser = Depends(require_permission(ESTRUCTURA_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[RolPermisoResponse]:
    repo = RolPermisoRepository(db, current_user.tenant_id)
    asignaciones = await repo.list()
    return [RolPermisoResponse.model_validate(a) for a in asignaciones]


@router.post("/roles", response_model=RolResponse, status_code=status.HTTP_201_CREATED)
async def create_rol(
    codigo: str,
    nombre: str,
    _: CurrentUser = Depends(require_permission(ESTRUCTURA_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> RolResponse:
    repo = RolRepository(db, current_user.tenant_id)
    existing = await repo.get_by_code(codigo)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Rol '{codigo}' already exists")
    rol = await repo.create(codigo=codigo, nombre=nombre)
    return RolResponse.model_validate(rol)


@router.post("/asignaciones", response_model=RolPermisoResponse, status_code=status.HTTP_201_CREATED)
async def assign_permiso(
    rol_id: str,
    permiso_id: str,
    alcance: str = "global",
    _: CurrentUser = Depends(require_permission(ESTRUCTURA_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> RolPermisoResponse:
    from uuid import UUID

    repo = RolPermisoRepository(db, current_user.tenant_id)
    rp = await repo.assign(rol_id=UUID(rol_id), permiso_id=UUID(permiso_id), alcance=alcance)
    return RolPermisoResponse.model_validate(rp)
