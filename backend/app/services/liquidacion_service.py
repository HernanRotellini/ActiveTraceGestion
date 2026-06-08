"""Servicio de cálculo y cierre de liquidaciones."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.liquidaciones import Liquidacion, RolLiquidacion, SegmentoLiquidacion
from app.repositories.liquidacion_repository import (
    LiquidacionContextRepository,
    LiquidacionRepository,
    MateriaPlusRepository,
    SalarioBaseRepository,
    SalarioPlusRepository,
)


class LiquidacionError(ValueError):
    """Error base de liquidaciones."""


class LiquidacionContextError(LiquidacionError):
    """Contexto inválido para el tenant."""


class LiquidacionMissingConfigurationError(LiquidacionError):
    """Falta configuración salarial vigente requerida."""


class LiquidacionAlreadyClosedError(LiquidacionError):
    """La liquidación ya está cerrada para cohorte y período."""


class LiquidacionNotFoundError(LiquidacionError):
    """Liquidación no encontrada en el tenant."""


@dataclass(frozen=True)
class LiquidacionPreviewItem:
    usuario_id: UUID
    rol: RolLiquidacion
    monto_base: Decimal
    monto_plus: Decimal
    monto_total: Decimal
    comisiones: list[str]
    es_nexo: bool
    excluido_por_factura: bool
    procesable: bool
    motivo_no_procesable: str | None = None


@dataclass(frozen=True)
class LiquidacionPreview:
    cohorte_id: UUID
    periodo: str
    items: list[LiquidacionPreviewItem]
    total_pagable: Decimal
    segmento_nexo_total: Decimal
    segmento_facturantes_total: Decimal


class LiquidacionService:
    """Calcula previews y persiste cierres sin consultas directas desde el servicio."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.tenant_id = tenant_id
        self._base_repo = SalarioBaseRepository(session, tenant_id)
        self._plus_repo = SalarioPlusRepository(session, tenant_id)
        self._materia_plus_repo = MateriaPlusRepository(session, tenant_id)
        self._liquidacion_repo = LiquidacionRepository(session, tenant_id)
        self._context_repo = LiquidacionContextRepository(session, tenant_id)

    async def preview(self, *, cohorte_id: UUID, periodo: str) -> LiquidacionPreview:
        periodo_date = self._periodo_to_date(periodo)
        if not await self._context_repo.cohorte_exists(cohorte_id):
            raise LiquidacionContextError("Cohorte inválida para el tenant")

        asignaciones = await self._context_repo.list_asignaciones_vigentes(cohorte_id=cohorte_id, periodo=periodo_date)
        usuarios = await self._context_repo.list_usuarios_by_ids({asignacion.usuario_id for asignacion in asignaciones})
        grouped: dict[tuple[UUID, RolLiquidacion], dict] = {}
        for asignacion in asignaciones:
            rol = self._to_rol_liquidacion(asignacion.rol)
            key = (asignacion.usuario_id, rol)
            grouped.setdefault(key, {"asignaciones": [], "comisiones": []})["asignaciones"].append(asignacion)
            grouped[key]["comisiones"].extend(list(asignacion.comisiones or []))

        items: list[LiquidacionPreviewItem] = []
        for (usuario_id, rol), data in sorted(grouped.items(), key=lambda item: (str(item[0][0]), item[0][1].value)):
            usuario = usuarios.get(usuario_id)
            if usuario is None:
                raise LiquidacionContextError("Usuario inválido para el tenant")
            base = await self._base_repo.get_vigente(rol=rol, periodo=periodo_date)
            if base is None:
                raise LiquidacionMissingConfigurationError(f"Falta salario base vigente para {rol.value}")
            monto_plus = Decimal("0.00")
            for asignacion in data["asignaciones"]:
                if asignacion.materia_id is None:
                    continue
                mapping = await self._materia_plus_repo.get_vigente(materia_id=asignacion.materia_id, periodo=periodo_date)
                if mapping is None:
                    continue
                plus = await self._plus_repo.get_vigente(rol=rol, grupo=mapping.grupo, periodo=periodo_date)
                if plus is None:
                    raise LiquidacionMissingConfigurationError(
                        f"Falta plus vigente para grupo {mapping.grupo} y rol {rol.value}"
                    )
                monto_plus += plus.monto * self._commission_count(asignacion.comisiones)
            procesable = bool(usuario.banco and (usuario.cbu or usuario.alias_cbu))
            motivo = None if procesable else "datos_bancarios_incompletos"
            monto_total = base.monto + monto_plus
            items.append(
                LiquidacionPreviewItem(
                    usuario_id=usuario_id,
                    rol=rol,
                    monto_base=base.monto,
                    monto_plus=monto_plus,
                    monto_total=monto_total,
                    comisiones=list(data["comisiones"]),
                    es_nexo=rol == RolLiquidacion.NEXO,
                    excluido_por_factura=usuario.facturador,
                    procesable=procesable,
                    motivo_no_procesable=motivo,
                )
            )

        return LiquidacionPreview(
            cohorte_id=cohorte_id,
            periodo=periodo,
            items=items,
            total_pagable=sum(
                (item.monto_total for item in items if item.procesable and not item.excluido_por_factura), Decimal("0.00")
            ),
            segmento_nexo_total=sum((item.monto_total for item in items if item.es_nexo), Decimal("0.00")),
            segmento_facturantes_total=sum(
                (item.monto_total for item in items if item.excluido_por_factura), Decimal("0.00")
            ),
        )

    async def close(self, *, cohorte_id: UUID, periodo: str, actor_id: UUID) -> list[Liquidacion]:
        if await self._liquidacion_repo.exists_closed(cohorte_id=cohorte_id, periodo=periodo):
            raise LiquidacionAlreadyClosedError("La liquidación ya está cerrada")
        preview = await self.preview(cohorte_id=cohorte_id, periodo=periodo)
        closed = [
            await self._liquidacion_repo.create_snapshot(
                cohorte_id=cohorte_id,
                usuario_id=item.usuario_id,
                periodo=periodo,
                rol=item.rol,
                monto_base=item.monto_base,
                monto_plus=item.monto_plus,
                monto_total=item.monto_total,
                comisiones=item.comisiones,
                es_nexo=item.es_nexo,
                excluido_por_factura=item.excluido_por_factura,
            )
            for item in preview.items
        ]
        await self._context_repo.create_audit(
            actor_id=actor_id,
            accion="LIQUIDACION_CERRAR",
            detalle={"cohorte_id": str(cohorte_id), "periodo": periodo},
            filas_afectadas=len(closed),
        )
        return closed

    async def list_closed(
        self,
        *,
        periodo: str | None = None,
        cohorte_id: UUID | None = None,
        usuario_id: UUID | None = None,
        segmento: SegmentoLiquidacion | None = None,
    ) -> list[Liquidacion]:
        return await self._liquidacion_repo.list_filtered(
            periodo=periodo, cohorte_id=cohorte_id, usuario_id=usuario_id, segmento=segmento
        )

    async def get(self, liquidacion_id: UUID) -> Liquidacion:
        liquidacion = await self._liquidacion_repo.get(liquidacion_id)
        if liquidacion is None:
            raise LiquidacionNotFoundError("Liquidación no encontrada")
        return liquidacion

    def _periodo_to_date(self, periodo: str) -> date:
        year, month = periodo.split("-", 1)
        return date(int(year), int(month), 1)

    def _to_rol_liquidacion(self, rol: str) -> RolLiquidacion:
        try:
            return RolLiquidacion(rol)
        except ValueError as exc:
            raise LiquidacionContextError(f"Rol {rol} no liquidable") from exc

    def _commission_count(self, comisiones: list | None) -> int:
        return len(comisiones) if comisiones else 1
