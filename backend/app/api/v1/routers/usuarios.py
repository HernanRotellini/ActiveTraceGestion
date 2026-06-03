"""Router para ABM de Usuarios."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.config import Settings
from app.core.dependencies import get_db, require_permission
from app.models.permisos import USUARIOS_GESTIONAR
from app.schemas.usuarios import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services.auth import CurrentUser
from app.services.usuarios import DuplicateEmailError, NotFoundError, UsuarioService

router = APIRouter(prefix="/api/admin/usuarios", tags=["usuarios"])

UsuariosGuard = Depends(require_permission(USUARIOS_GESTIONAR))

settings = Settings()  # type: ignore[call-arg]


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    body: UsuarioCreate,
    _: CurrentUser = UsuariosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> UsuarioResponse:
    service = UsuarioService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    try:
        usuario = await service.create_usuario(**body.model_dump())
    except DuplicateEmailError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return UsuarioResponse.model_validate(usuario)


@router.get("", response_model=list[UsuarioResponse])
async def list_usuarios(
    _: CurrentUser = UsuariosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[UsuarioResponse]:
    service = UsuarioService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    usuarios = await service.list_usuarios()
    return [UsuarioResponse.model_validate(u) for u in usuarios]


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: UUID,
    _: CurrentUser = UsuariosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> UsuarioResponse:
    service = UsuarioService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    usuario = await service.get_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario not found")
    return UsuarioResponse.model_validate(usuario)


@router.patch("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: UUID,
    body: UsuarioUpdate,
    _: CurrentUser = UsuariosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> UsuarioResponse:
    service = UsuarioService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    try:
        usuario = await service.update_usuario(usuario_id, **body.model_dump(exclude_none=True))
    except DuplicateEmailError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return UsuarioResponse.model_validate(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: UUID,
    _: CurrentUser = UsuariosGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    service = UsuarioService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    deleted = await service.delete_usuario(usuario_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario not found")
