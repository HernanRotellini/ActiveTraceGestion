"""Router de perfil propio del usuario autenticado.

Cualquier usuario autenticado puede ver y editar su propio perfil.
No requiere permisos especiales — la identidad se resuelve desde el JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.config import Settings
from app.core.dependencies import get_db
from app.schemas.perfil import PerfilResponse, PerfilUpdate
from app.services.auth import CurrentUser
from app.services.perfil_service import DuplicateEmailError, PerfilService

router = APIRouter(prefix="/api/v1/perfil", tags=["perfil"])

settings = Settings()  # type: ignore[call-arg]


@router.get("", response_model=PerfilResponse)
async def get_perfil(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PerfilResponse:
    service = PerfilService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    usuario = await service.get_perfil(current_user.user_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario not found")
    return PerfilResponse.model_validate(usuario)


@router.put("", response_model=PerfilResponse)
async def update_perfil(
    body: PerfilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> PerfilResponse:
    service = PerfilService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    try:
        usuario = await service.update_perfil(current_user.user_id, **body.model_dump(exclude_none=True))
    except DuplicateEmailError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario not found")
    return PerfilResponse.model_validate(usuario)
