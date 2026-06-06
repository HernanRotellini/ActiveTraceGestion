"""Router para el módulo de encuentros sincrónicos."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import ENCUENTROS_GESTIONAR
from app.schemas.encuentro import (
    HtmlBlockResponse,
    InstanciaEncuentroCreate,
    InstanciaEncuentroResponse,
    InstanciaEncuentroUpdate,
    SlotEncuentroCreate,
    SlotEncuentroResponse,
)
from app.services.auth import CurrentUser
from app.services.encuentro_service import EncuentroError, EncuentroService

router = APIRouter(prefix="/api/v1/encuentros", tags=["encuentros"])

Guard = Depends(require_permission(ENCUENTROS_GESTIONAR))


@router.post("/slots", response_model=SlotEncuentroResponse, status_code=status.HTTP_201_CREATED)
async def crear_slot(
    body: SlotEncuentroCreate,
    _: CurrentUser = Guard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> SlotEncuentroResponse:
    """Crea un slot de encuentro recurrente con generación de instancias."""
    service = EncuentroService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.crear_slot_recurrente(
            asignacion_id=body.asignacion_id,
            materia_id=body.materia_id,
            titulo=body.titulo,
            dia_semana=body.dia_semana,
            hora=body.hora,
            fecha_inicio=body.fecha_inicio,
            cant_semanas=body.cant_semanas,
            meet_url=body.meet_url,
            vig_desde=body.vig_desde,
        )
    except EncuentroError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return SlotEncuentroResponse(**result)


@router.get("/slots", response_model=list[SlotEncuentroResponse])
async def listar_slots(
    materia_id: UUID | None = Query(None),
    _: CurrentUser = Guard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[SlotEncuentroResponse]:
    """Lista slots de encuentro del tenant."""
    service = EncuentroService(db, current_user.tenant_id, current_user.user_id)
    slots = await service.repo.listar_slots(materia_id)
    return [SlotEncuentroResponse.model_validate(s) for s in slots]


@router.post("/instancias", response_model=InstanciaEncuentroResponse, status_code=status.HTTP_201_CREATED)
async def crear_instancia_unica(
    body: InstanciaEncuentroCreate,
    _: CurrentUser = Guard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> InstanciaEncuentroResponse:
    """Crea una instancia de encuentro único (sin slot asociado)."""
    service = EncuentroService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.crear_instancia_unica(
            materia_id=body.materia_id,
            fecha=body.fecha,
            hora=body.hora,
            titulo=body.titulo,
            meet_url=body.meet_url,
        )
    except EncuentroError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return InstanciaEncuentroResponse(**result)


@router.get("/instancias", response_model=list[InstanciaEncuentroResponse])
async def listar_instancias(
    materia_id: UUID | None = Query(None),
    _: CurrentUser = Guard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[InstanciaEncuentroResponse]:
    """Lista instancias de encuentro del tenant."""
    service = EncuentroService(db, current_user.tenant_id, current_user.user_id)
    instancias = await service.repo.listar_instancias(materia_id)
    return [InstanciaEncuentroResponse.model_validate(i) for i in instancias]


@router.patch("/instancias/{instancia_id}", response_model=InstanciaEncuentroResponse)
async def actualizar_instancia(
    instancia_id: UUID,
    body: InstanciaEncuentroUpdate,
    _: CurrentUser = Guard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> InstanciaEncuentroResponse:
    """Actualiza estado, meet_url, video_url o comentario de una instancia."""
    service = EncuentroService(db, current_user.tenant_id, current_user.user_id)
    try:
        result = await service.actualizar_instancia(
            instancia_id=instancia_id,
            estado=body.estado,
            meet_url=body.meet_url,
            video_url=body.video_url,
            comentario=body.comentario,
        )
    except EncuentroError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return InstanciaEncuentroResponse(**result)


@router.get("/instancias/{instancia_id}/html", response_model=HtmlBlockResponse)
async def generar_html(
    instancia_id: UUID,
    _: CurrentUser = Guard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> HtmlBlockResponse:
    """Genera bloque HTML con encuentros de una materia."""
    service = EncuentroService(db, current_user.tenant_id, current_user.user_id)
    instancia = await service.repo.get_instancia(instancia_id)
    if instancia is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instancia no encontrada")
    html = await service.generar_html_block(instancia.materia_id)
    return HtmlBlockResponse(html=html)


@router.get("/admin/instancias", response_model=list[InstanciaEncuentroResponse])
async def admin_listar_instancias(
    materia_id: UUID | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    estado: str | None = Query(None),
    _: CurrentUser = Guard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[InstanciaEncuentroResponse]:
    """Vista admin transversal de todas las instancias del tenant con filtros."""
    service = EncuentroService(db, current_user.tenant_id, current_user.user_id)
    result = await service.listar_admin(
        materia_id=materia_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        estado=estado,
    )
    return [InstanciaEncuentroResponse(**item) for item in result]
