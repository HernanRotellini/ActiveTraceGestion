"""Servicio de facturas docentes."""

from dataclasses import dataclass
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


@dataclass(frozen=True)
class FacturaDetalle:
    id: UUID
    usuario_id: UUID
    usuario_nombre: str
    usuario_apellidos: str
    usuario_roles: list[str]
    periodo: str
    detalle: str
    referencia_archivo: str
    archivo_size_bytes: int
    estado: EstadoFactura
    abonada_at: datetime | None
    created_at: datetime


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
    ) -> FacturaDetalle:
        usuario = await self._context_repo.get_usuario(usuario_id)
        if usuario is None:
            raise FacturaNotFoundError("Usuario facturante no encontrado")
        if not usuario.facturador:
            raise FacturaUsuarioNoFacturanteError("El usuario no es facturante del tenant")
        factura = await self._repo.create(
            usuario_id=usuario_id,
            periodo=periodo,
            detalle=detalle,
            referencia_archivo=referencia_archivo,
            archivo_size_bytes=archivo_size_bytes,
        )
        return await self._build_factura_detalle(factura, usuario=usuario)

    async def list_facturas(
        self,
        *,
        usuario_id: UUID | None = None,
        periodo: str | None = None,
        estado: EstadoFactura | None = None,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> list[FacturaDetalle]:
        facturas = await self._repo.list_filtered(
            usuario_id=usuario_id,
            periodo=periodo,
            estado=estado,
            desde=desde,
            hasta=hasta,
        )
        return await self._build_factura_detalles(facturas)

    async def get_factura(self, factura_id: UUID) -> FacturaDetalle:
        factura = await self._repo.get(factura_id)
        if factura is None:
            raise FacturaNotFoundError("Factura no encontrada")
        return await self._build_factura_detalle(factura)

    async def update_factura(
        self,
        factura_id: UUID,
        *,
        periodo: str | None = None,
        detalle: str | None = None,
        referencia_archivo: str | None = None,
        archivo_size_bytes: int | None = None,
    ) -> FacturaDetalle:
        factura = await self._repo.update(
            factura_id,
            periodo=periodo,
            detalle=detalle,
            referencia_archivo=referencia_archivo,
            archivo_size_bytes=archivo_size_bytes,
        )
        if factura is None:
            raise FacturaNotFoundError("Factura no encontrada")
        return await self._build_factura_detalle(factura)

    async def delete_factura(self, factura_id: UUID) -> None:
        if not await self._repo.soft_delete(factura_id):
            raise FacturaNotFoundError("Factura no encontrada")

    async def mark_abonada(self, factura_id: UUID, *, abonada_at: datetime | None = None) -> FacturaDetalle:
        factura = await self._repo.get(factura_id)
        if factura is None:
            raise FacturaNotFoundError("Factura no encontrada")
        if factura.estado != EstadoFactura.PENDIENTE:
            raise FacturaInvalidTransitionError("Solo una factura pendiente puede marcarse abonada")
        updated = await self._repo.mark_abonada(factura_id, abonada_at=abonada_at)
        if updated is None:
            raise FacturaNotFoundError("Factura no encontrada")
        return await self._build_factura_detalle(updated)

    async def _build_factura_detalles(self, facturas: list[Factura]) -> list[FacturaDetalle]:
        usuarios = await self._context_repo.list_usuarios_by_ids({factura.usuario_id for factura in facturas})
        roles_by_usuario = await self._context_repo.list_roles_by_usuario_ids(set(usuarios.keys()))
        detalles: list[FacturaDetalle] = []
        for factura in facturas:
            usuario = usuarios.get(factura.usuario_id)
            if usuario is None:
                raise FacturaNotFoundError("Usuario facturante no encontrado")
            detalles.append(
                FacturaDetalle(
                    id=factura.id,
                    usuario_id=factura.usuario_id,
                    usuario_nombre=usuario.nombre,
                    usuario_apellidos=usuario.apellidos,
                    usuario_roles=roles_by_usuario.get(factura.usuario_id, []),
                    periodo=factura.periodo,
                    detalle=factura.detalle,
                    referencia_archivo=factura.referencia_archivo,
                    archivo_size_bytes=factura.archivo_size_bytes,
                    estado=factura.estado,
                    abonada_at=factura.abonada_at,
                    created_at=factura.created_at,
                )
            )
        return detalles

    async def _build_factura_detalle(self, factura: Factura, *, usuario=None) -> FacturaDetalle:
        if usuario is None:
            usuario = await self._context_repo.get_usuario(factura.usuario_id)
        if usuario is None:
            raise FacturaNotFoundError("Usuario facturante no encontrado")
        roles_by_usuario = await self._context_repo.list_roles_by_usuario_ids({factura.usuario_id})
        return FacturaDetalle(
            id=factura.id,
            usuario_id=factura.usuario_id,
            usuario_nombre=usuario.nombre,
            usuario_apellidos=usuario.apellidos,
            usuario_roles=roles_by_usuario.get(factura.usuario_id, []),
            periodo=factura.periodo,
            detalle=factura.detalle,
            referencia_archivo=factura.referencia_archivo,
            archivo_size_bytes=factura.archivo_size_bytes,
            estado=factura.estado,
            abonada_at=factura.abonada_at,
            created_at=factura.created_at,
        )
