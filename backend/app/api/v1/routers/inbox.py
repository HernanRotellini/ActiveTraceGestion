"""Router de mensajería interna (inbox).

Cualquier usuario autenticado puede ver sus hilos, crear nuevos hilos
y responder. El filtro de acceso es por pertenencia al hilo (participante).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.config import Settings
from app.core.dependencies import get_db
from app.schemas.inbox import CrearHiloRequest, HiloResponse, MensajeResponse, ResponderRequest
from app.services.auth import CurrentUser
from app.services.inbox_service import InboxService, NotFoundError

router = APIRouter(prefix="/api/v1/inbox", tags=["inbox"])

settings = Settings()  # type: ignore[call-arg]


@router.get("", response_model=list[HiloResponse])
async def list_inbox(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[HiloResponse]:
    service = InboxService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    hilos = await service.list_threads(current_user.user_id)
    return [HiloResponse(**h) for h in hilos]


@router.get("/{hilo_id}", response_model=HiloResponse)
async def get_hilo(
    hilo_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> HiloResponse:
    service = InboxService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    hilo = await service.get_thread(hilo_id, current_user.user_id)
    if hilo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    return HiloResponse(**hilo)


@router.post("", response_model=HiloResponse, status_code=status.HTTP_201_CREATED)
async def create_hilo(
    body: CrearHiloRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> HiloResponse:
    service = InboxService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    try:
        hilo = await service.create_thread(
            remitente_id=current_user.user_id,
            asunto=body.asunto,
            destinatarios=body.destinatarios,
            cuerpo=body.cuerpo,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return HiloResponse(**hilo)


@router.post("/{hilo_id}/responder", response_model=MensajeResponse, status_code=status.HTTP_201_CREATED)
async def responder_hilo(
    hilo_id: UUID,
    body: ResponderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> MensajeResponse:
    service = InboxService(db, current_user.tenant_id, settings.ENCRYPTION_KEY)
    mensaje = await service.reply_to_thread(
        hilo_id=hilo_id,
        remitente_id=current_user.user_id,
        cuerpo=body.cuerpo,
    )
    if mensaje is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")
    return MensajeResponse(**mensaje)
