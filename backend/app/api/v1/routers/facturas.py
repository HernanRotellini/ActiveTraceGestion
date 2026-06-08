"""Router para facturas docentes."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.routers.rbac import CurrentUserDep
from app.core.dependencies import get_db, require_permission
from app.models.liquidaciones import EstadoFactura
from app.models.permisos import FACTURAS_GESTIONAR
from app.schemas.liquidaciones import FacturaCreate, FacturaResponse, FacturaUpdate
from app.services.auth import CurrentUser
from app.services.factura_service import (
    FacturaInvalidTransitionError,
    FacturaNotFoundError,
    FacturaService,
    FacturaUsuarioNoFacturanteError,
)

router = APIRouter(prefix="/api/facturas", tags=["facturas"])

FacturasGuard = Depends(require_permission(FACTURAS_GESTIONAR))


def _service(db: AsyncSession, current_user: CurrentUser) -> FacturaService:
    return FacturaService(db, current_user.tenant_id)


@router.post("", response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
async def create_factura(
    body: FacturaCreate,
    _: CurrentUser = FacturasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> FacturaResponse:
    try:
        factura = await _service(db, current_user).register_factura(
            usuario_id=body.usuario_id,
            periodo=body.periodo,
            detalle=body.detalle,
            referencia_archivo=body.referencia_archivo,
            archivo_size_bytes=body.archivo_size_bytes,
        )
    except FacturaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FacturaUsuarioNoFacturanteError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return FacturaResponse.model_validate(factura)


@router.get("", response_model=list[FacturaResponse])
async def list_facturas(
    _: CurrentUser = FacturasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
    usuario_id: UUID | None = Query(default=None),
    periodo: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    estado: EstadoFactura | None = Query(default=None),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
) -> list[FacturaResponse]:
    facturas = await _service(db, current_user).list_facturas(
        usuario_id=usuario_id, periodo=periodo, estado=estado, desde=desde, hasta=hasta
    )
    return [FacturaResponse.model_validate(factura) for factura in facturas]


@router.get("/{factura_id}", response_model=FacturaResponse)
async def get_factura(
    factura_id: UUID,
    _: CurrentUser = FacturasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> FacturaResponse:
    try:
        factura = await _service(db, current_user).get_factura(factura_id)
    except FacturaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FacturaResponse.model_validate(factura)


@router.put("/{factura_id}", response_model=FacturaResponse)
async def update_factura(
    factura_id: UUID,
    body: FacturaUpdate,
    _: CurrentUser = FacturasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> FacturaResponse:
    try:
        factura = await _service(db, current_user).update_factura(
            factura_id,
            periodo=body.periodo,
            detalle=body.detalle,
            referencia_archivo=body.referencia_archivo,
            archivo_size_bytes=body.archivo_size_bytes,
        )
    except FacturaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return FacturaResponse.model_validate(factura)


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_factura(
    factura_id: UUID,
    _: CurrentUser = FacturasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> None:
    try:
        await _service(db, current_user).delete_factura(factura_id)
    except FacturaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{factura_id}/abonada", response_model=FacturaResponse)
async def mark_factura_abonada(
    factura_id: UUID,
    _: CurrentUser = FacturasGuard,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = CurrentUserDep,
) -> FacturaResponse:
    try:
        factura = await _service(db, current_user).mark_abonada(factura_id)
    except FacturaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except FacturaInvalidTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return FacturaResponse.model_validate(factura)
