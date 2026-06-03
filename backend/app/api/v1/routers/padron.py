"""Router de operaciones de padrón de alumnos."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import get_current_user, get_db
from app.schemas.padron import (
    ImportConfirmRequest,
    ImportConfirmResponse,
    ImportPreviewResponse,
    VaciarResponse,
    VersionPadronList,
    VersionPadronResponse,
)
from app.services.auth import CurrentUser
from app.services.padron import PadronError, PadronService, PreviewExpiredError

router = APIRouter(prefix="/api/v1/padron", tags=["padron"])


@router.post("/preview", response_model=ImportPreviewResponse)
async def preview_importar(
    materia_id: str = Form(...),
    cohorte_id: str = Form(...),
    archivo: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Paso 1: Sube un archivo de padrón y devuelve preview con token."""
    if archivo.filename is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Filename is required")

    contenido = await archivo.read()
    settings = Settings()  # type: ignore[call-arg]
    service = PadronService(
        session=db,
        tenant_id=current_user.tenant_id,
        current_user_id=current_user.user_id,
        encryption_key=settings.ENCRYPTION_KEY,
    )

    try:
        result = await service.preview_importar(materia_id, cohorte_id, archivo.filename, contenido)
    except PadronError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return result


@router.post("/confirmar", response_model=ImportConfirmResponse)
async def confirmar_importar(
    payload: ImportConfirmRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Paso 2: Confirma la importación usando un token de preview."""
    settings = Settings()  # type: ignore[call-arg]
    service = PadronService(
        session=db,
        tenant_id=current_user.tenant_id,
        current_user_id=current_user.user_id,
        encryption_key=settings.ENCRYPTION_KEY,
    )

    try:
        result = await service.confirmar_importar(payload.preview_token)
    except PreviewExpiredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except PadronError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return result


@router.get("/materias/{materia_id}/versiones", response_model=VersionPadronList)
async def listar_versiones(
    materia_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Lista versiones de padrón para una materia."""
    settings = Settings()  # type: ignore[call-arg]
    service = PadronService(
        session=db,
        tenant_id=current_user.tenant_id,
        current_user_id=current_user.user_id,
        encryption_key=settings.ENCRYPTION_KEY,
    )
    return await service.listar_versiones(materia_id, page=page, size=size)


@router.delete("/materias/{materia_id}/vaciar", response_model=VaciarResponse)
async def vaciar_materia(
    materia_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Vacía los datos de padrón del usuario actual para una materia (RN-04)."""
    settings = Settings()  # type: ignore[call-arg]
    service = PadronService(
        session=db,
        tenant_id=current_user.tenant_id,
        current_user_id=current_user.user_id,
        encryption_key=settings.ENCRYPTION_KEY,
    )
    return await service.vaciar_materia(materia_id)
