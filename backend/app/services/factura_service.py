"""Servicio de facturas docentes."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.liquidaciones import EstadoFactura, Factura
from app.repositories.liquidacion_repository import FacturaRepository, LiquidacionContextRepository


class FacturaError(ValueError):
    """Error base de facturas."""


class FacturaNotFoundError(FacturaError):
    """Factura no encontrada en el tenant."""


class FacturaUsuarioNoFacturanteError(FacturaError):
    """Usuario inválido o no configurado como facturante."""


class FacturaInvalidTransitionError(FacturaError):
    """Transición de estado inválida."""


class FacturaService:
    """Orquesta facturas docentes sin consultas directas desde el servicio."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = FacturaRepository(session, tenant_id)
        self._context_repo = LiquidacionContextRepository(session, tenant_id)

    async def register_factura(
        self,
        *,
        usuario_id: UUID,
        periodo: str,
        detalle: str,
        referencia_archivo: str,
        archivo_size_bytes: int,
    ) -> Factura:
        usuario = await self._context_repo.get_usuario(usuario_id)
        if usuario is None:
            raise FacturaNotFoundError("Usuario facturante no encontrado")
        if not usuario.facturador:
            raise FacturaUsuarioNoFacturanteError("El usuario no es facturante del tenant")
        return await self._repo.create(
            usuario_id=usuario_id,
            periodo=periodo,
            detalle=detalle,
            referencia_archivo=referencia_archivo,
            archivo_size_bytes=archivo_size_bytes,
        )

    async def list_facturas(
        self,
        *,
        usuario_id: UUID | None = None,
        periodo: str | None = None,
        estado: EstadoFactura | None = None,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> list[Factura]:
        return await self._repo.list_filtered(usuario_id=usuario_id, periodo=periodo, estado=estado, desde=desde, hasta=hasta)

    async def get_factura(self, factura_id: UUID) -> Factura:
        factura = await self._repo.get(factura_id)
        if factura is None:
            raise FacturaNotFoundError("Factura no encontrada")
        return factura

    async def update_factura(
        self,
        factura_id: UUID,
        *,
        periodo: str | None = None,
        detalle: str | None = None,
        referencia_archivo: str | None = None,
        archivo_size_bytes: int | None = None,
    ) -> Factura:
        factura = await self._repo.update(
            factura_id,
            periodo=periodo,
            detalle=detalle,
            referencia_archivo=referencia_archivo,
            archivo_size_bytes=archivo_size_bytes,
        )
        if factura is None:
            raise FacturaNotFoundError("Factura no encontrada")
        return factura

    async def delete_factura(self, factura_id: UUID) -> None:
        if not await self._repo.soft_delete(factura_id):
            raise FacturaNotFoundError("Factura no encontrada")

    async def mark_abonada(self, factura_id: UUID, *, abonada_at: datetime | None = None) -> Factura:
        factura = await self._repo.get(factura_id)
        if factura is None:
            raise FacturaNotFoundError("Factura no encontrada")
        if factura.estado != EstadoFactura.PENDIENTE:
            raise FacturaInvalidTransitionError("Solo una factura pendiente puede marcarse abonada")
        updated = await self._repo.mark_abonada(factura_id, abonada_at=abonada_at)
        if updated is None:
            raise FacturaNotFoundError("Factura no encontrada")
        return updated
