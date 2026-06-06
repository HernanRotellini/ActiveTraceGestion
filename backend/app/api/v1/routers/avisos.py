"""Router para el módulo de avisos institucionales.

Endpoints públicos (autenticado):
  - GET  /api/avisos             → listar visibles
  - GET  /api/avisos/pendientes-ack → pendientes de confirmación
  - POST /api/avisos/{id}/ack    → confirmar lectura

Endpoints de gestión (permiso avisos:publicar):
  - GET    /api/admin/avisos           → listar todos
  - POST   /api/admin/avisos           → crear
  - GET    /api/admin/avisos/{id}      → detalle
  - PUT    /api/admin/avisos/{id}      → actualizar
  - DELETE /api/admin/avisos/{id}      → desactivar
  - GET    /api/admin/avisos/{id}/stats → estadísticas
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.permisos import AVISOS_PUBLICAR
from app.schemas.aviso import (
    AvisoCreate,
    AvisoListResponse,
    AvisoResponse,
    AvisoStatsResponse,
    AvisoUpdate,
)
from app.services.auth import CurrentUser
from app.services.aviso_service import AvisoNotFoundError, AvisoService

router = APIRouter(tags=["avisos"])

AdminGuard = Depends(require_permission(AVISOS_PUBLICAR))


# ─────────────────────────────────────────────────────────────
# Endpoints públicos (autenticado)
# ─────────────────────────────────────────────────────────────


@router.get("/api/avisos", response_model=list[AvisoListResponse])
async def listar_avisos_visibles(
    materia_id: UUID | None = Query(None),
    cohorte_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[AvisoListResponse]:
    """Lista avisos visibles para el usuario autenticado.

    Filtra por rol, materia y cohorte según el perfil del usuario.
    Opcionalmente se pueden pasar materia_id y cohorte_id para
    acotar la búsqueda.
    """
    service = AvisoService(db, current_user.tenant_id)
    materia_ids = [materia_id] if materia_id else None
    cohorte_ids = [cohorte_id] if cohorte_id else None

    avisos = await service.listar_visibles(
        roles=current_user.roles,
        materia_ids=materia_ids,
        cohorte_ids=cohorte_ids,
    )
    return [AvisoListResponse.model_validate(a) for a in avisos]


@router.get("/api/avisos/pendientes-ack", response_model=list[AvisoListResponse])
async def listar_pendientes_ack(
    materia_id: UUID | None = Query(None),
    cohorte_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[AvisoListResponse]:
    """Lista avisos visibles que requieren ack y no han sido confirmados."""
    service = AvisoService(db, current_user.tenant_id)
    materia_ids = [materia_id] if materia_id else None
    cohorte_ids = [cohorte_id] if cohorte_id else None

    avisos = await service.listar_pendientes_ack(
        usuario_id=current_user.user_id,
        roles=current_user.roles,
        materia_ids=materia_ids,
        cohorte_ids=cohorte_ids,
    )
    return [AvisoListResponse.model_validate(a) for a in avisos]


@router.post("/api/avisos/{aviso_id}/ack", status_code=status.HTTP_204_NO_CONTENT)
async def confirmar_lectura(
    aviso_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    """Confirma lectura de un aviso. Idempotente."""
    service = AvisoService(db, current_user.tenant_id)

    aviso = await service.obtener_por_id(aviso_id)
    if aviso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso not found",
        )

    await service.confirmar_lectura(aviso_id, current_user.user_id)


# ─────────────────────────────────────────────────────────────
# Endpoints de gestión (avisos:publicar)
# ─────────────────────────────────────────────────────────────


@router.get("/api/admin/avisos", response_model=list[AvisoResponse])
async def listar_avisos_admin(
    alcance: str | None = Query(None),
    severidad: str | None = Query(None),
    activo: bool | None = Query(None),
    _: None = AdminGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> list[AvisoResponse]:
    """Lista todos los avisos del tenant (incluyendo inactivos)."""
    service = AvisoService(db, current_user.tenant_id)
    avisos = await service.listar_admin(
        alcance=alcance,
        severidad=severidad,
        activo=activo,
    )
    return [AvisoResponse.model_validate(a) for a in avisos]


@router.post("/api/admin/avisos", response_model=AvisoResponse, status_code=status.HTTP_201_CREATED)
async def crear_aviso(
    body: AvisoCreate,
    _: None = AdminGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AvisoResponse:
    """Crea un nuevo aviso."""
    service = AvisoService(db, current_user.tenant_id)
    aviso = await service.crear(
        datos=body.model_dump(),
        actor_id=current_user.user_id,
    )
    return AvisoResponse.model_validate(aviso)


@router.get("/api/admin/avisos/{aviso_id}", response_model=AvisoResponse)
async def obtener_aviso(
    aviso_id: UUID,
    _: None = AdminGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AvisoResponse:
    """Obtiene detalle de un aviso."""
    service = AvisoService(db, current_user.tenant_id)
    aviso = await service.obtener_por_id(aviso_id)
    if aviso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso not found",
        )
    return AvisoResponse.model_validate(aviso)


@router.put("/api/admin/avisos/{aviso_id}", response_model=AvisoResponse)
async def actualizar_aviso(
    aviso_id: UUID,
    body: AvisoUpdate,
    _: None = AdminGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AvisoResponse:
    """Actualiza un aviso existente."""
    service = AvisoService(db, current_user.tenant_id)
    try:
        aviso = await service.actualizar(
            aviso_id=aviso_id,
            datos=body.model_dump(exclude_unset=True),
            actor_id=current_user.user_id,
        )
    except AvisoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso not found",
        )
    return AvisoResponse.model_validate(aviso)


@router.delete("/api/admin/avisos/{aviso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_aviso(
    aviso_id: UUID,
    _: None = AdminGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    """Desactiva un aviso (soft delete)."""
    service = AvisoService(db, current_user.tenant_id)
    try:
        await service.desactivar(aviso_id, current_user.user_id)
    except AvisoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso not found",
        )


@router.get("/api/admin/avisos/{aviso_id}/stats", response_model=AvisoStatsResponse)
async def obtener_stats_aviso(
    aviso_id: UUID,
    _: None = AdminGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> AvisoStatsResponse:
    """Obtiene estadísticas de confirmación de un aviso."""
    service = AvisoService(db, current_user.tenant_id)
    aviso = await service.obtener_por_id(aviso_id)
    if aviso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aviso not found",
        )

    stats = await service.obtener_stats(aviso_id)
    return AvisoStatsResponse(**stats)
