"""Repositorios tenant-scoped para liquidaciones y honorarios."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.estructura_academica import Cohorte, Materia
from app.models.liquidaciones import (
    EstadoFactura,
    EstadoLiquidacion,
    Factura,
    Liquidacion,
    MateriaPlus,
    RolLiquidacion,
    SalarioBase,
    SalarioPlus,
    SegmentoLiquidacion,
)
from app.models.usuarios_asignaciones import Asignacion, Usuario
from app.repositories.base import TenantScopedRepository


MAX_DATE = date(9999, 12, 31)


def _active_at(model, periodo: date):
    return model.desde <= periodo, or_(model.hasta.is_(None), model.hasta >= periodo)


def _overlaps(model, desde: date, hasta: date | None):
    hasta_cmp = hasta or MAX_DATE
    return model.desde <= hasta_cmp, or_(model.hasta.is_(None), model.hasta >= desde)


class SalarioBaseRepository(TenantScopedRepository[SalarioBase]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, SalarioBase, tenant_id)

    async def create(
        self, *, rol: RolLiquidacion, monto: Decimal, desde: date, hasta: date | None = None
    ) -> SalarioBase:
        record = SalarioBase(tenant_id=self.tenant_id, rol=rol, monto=monto, desde=desde, hasta=hasta)
        self.session.add(record)
        await self.session.flush()
        return record

    async def update(
        self,
        record_id: UUID,
        *,
        rol: RolLiquidacion | None = None,
        monto: Decimal | None = None,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> SalarioBase | None:
        record = await self.get(record_id)
        if record is None:
            return None
        if rol is not None:
            record.rol = rol
        if monto is not None:
            record.monto = monto
        if desde is not None:
            record.desde = desde
        if hasta is not None:
            record.hasta = hasta
        return record

    async def get_vigente(self, *, rol: RolLiquidacion, periodo: date) -> SalarioBase | None:
        result = await self.session.execute(
            select(SalarioBase).where(
                SalarioBase.tenant_id == self.tenant_id,
                SalarioBase.deleted_at.is_(None),
                SalarioBase.rol == rol,
                *_active_at(SalarioBase, periodo),
            )
        )
        return result.scalar_one_or_none()

    async def has_overlap(
        self, *, rol: RolLiquidacion, desde: date, hasta: date | None, exclude_id: UUID | None = None
    ) -> bool:
        where = [
            SalarioBase.tenant_id == self.tenant_id,
            SalarioBase.deleted_at.is_(None),
            SalarioBase.rol == rol,
            *_overlaps(SalarioBase, desde, hasta),
        ]
        if exclude_id is not None:
            where.append(SalarioBase.id != exclude_id)
        result = await self.session.execute(select(SalarioBase.id).where(*where).limit(1))
        return result.scalar_one_or_none() is not None


class SalarioPlusRepository(TenantScopedRepository[SalarioPlus]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, SalarioPlus, tenant_id)

    async def create(
        self,
        *,
        rol: RolLiquidacion,
        grupo: str,
        descripcion: str,
        monto: Decimal,
        desde: date,
        hasta: date | None = None,
    ) -> SalarioPlus:
        record = SalarioPlus(
            tenant_id=self.tenant_id,
            rol=rol,
            grupo=grupo,
            descripcion=descripcion,
            monto=monto,
            desde=desde,
            hasta=hasta,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_vigente(self, *, rol: RolLiquidacion, grupo: str, periodo: date) -> SalarioPlus | None:
        result = await self.session.execute(
            select(SalarioPlus).where(
                SalarioPlus.tenant_id == self.tenant_id,
                SalarioPlus.deleted_at.is_(None),
                SalarioPlus.rol == rol,
                SalarioPlus.grupo == grupo,
                *_active_at(SalarioPlus, periodo),
            )
        )
        return result.scalar_one_or_none()

    async def has_overlap(
        self, *, rol: RolLiquidacion, grupo: str, desde: date, hasta: date | None, exclude_id: UUID | None = None
    ) -> bool:
        where = [
            SalarioPlus.tenant_id == self.tenant_id,
            SalarioPlus.deleted_at.is_(None),
            SalarioPlus.rol == rol,
            SalarioPlus.grupo == grupo,
            *_overlaps(SalarioPlus, desde, hasta),
        ]
        if exclude_id is not None:
            where.append(SalarioPlus.id != exclude_id)
        result = await self.session.execute(select(SalarioPlus.id).where(*where).limit(1))
        return result.scalar_one_or_none() is not None


class MateriaPlusRepository(TenantScopedRepository[MateriaPlus]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, MateriaPlus, tenant_id)

    async def create(self, *, materia_id: UUID, grupo: str, desde: date, hasta: date | None = None) -> MateriaPlus:
        record = MateriaPlus(tenant_id=self.tenant_id, materia_id=materia_id, grupo=grupo, desde=desde, hasta=hasta)
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_vigente(self, *, materia_id: UUID, periodo: date) -> MateriaPlus | None:
        result = await self.session.execute(
            select(MateriaPlus).where(
                MateriaPlus.tenant_id == self.tenant_id,
                MateriaPlus.deleted_at.is_(None),
                MateriaPlus.materia_id == materia_id,
                *_active_at(MateriaPlus, periodo),
            )
        )
        return result.scalar_one_or_none()

    async def has_overlap(
        self, *, materia_id: UUID, desde: date, hasta: date | None, exclude_id: UUID | None = None
    ) -> bool:
        where = [
            MateriaPlus.tenant_id == self.tenant_id,
            MateriaPlus.deleted_at.is_(None),
            MateriaPlus.materia_id == materia_id,
            *_overlaps(MateriaPlus, desde, hasta),
        ]
        if exclude_id is not None:
            where.append(MateriaPlus.id != exclude_id)
        result = await self.session.execute(select(MateriaPlus.id).where(*where).limit(1))
        return result.scalar_one_or_none() is not None


class LiquidacionRepository(TenantScopedRepository[Liquidacion]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Liquidacion, tenant_id)

    async def create_snapshot(
        self,
        *,
        cohorte_id: UUID,
        usuario_id: UUID,
        periodo: str,
        rol: RolLiquidacion,
        monto_base: Decimal,
        monto_plus: Decimal,
        monto_total: Decimal,
        comisiones: list[str],
        es_nexo: bool = False,
        excluido_por_factura: bool = False,
    ) -> Liquidacion:
        record = Liquidacion(
            tenant_id=self.tenant_id,
            cohorte_id=cohorte_id,
            usuario_id=usuario_id,
            periodo=periodo,
            rol=rol,
            estado=EstadoLiquidacion.CERRADA,
            monto_base=monto_base,
            monto_plus=monto_plus,
            monto_total=monto_total,
            comisiones=comisiones,
            es_nexo=es_nexo,
            excluido_por_factura=excluido_por_factura,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_filtered(
        self,
        *,
        periodo: str | None = None,
        cohorte_id: UUID | None = None,
        usuario_id: UUID | None = None,
        estado: EstadoLiquidacion | None = None,
        segmento: SegmentoLiquidacion | None = None,
    ) -> list[Liquidacion]:
        where = [Liquidacion.tenant_id == self.tenant_id, Liquidacion.deleted_at.is_(None)]
        if periodo is not None:
            where.append(Liquidacion.periodo == periodo)
        if cohorte_id is not None:
            where.append(Liquidacion.cohorte_id == cohorte_id)
        if usuario_id is not None:
            where.append(Liquidacion.usuario_id == usuario_id)
        if estado is not None:
            where.append(Liquidacion.estado == estado)
        if segmento == SegmentoLiquidacion.FACTURANTE:
            where.append(Liquidacion.excluido_por_factura.is_(True))
        elif segmento == SegmentoLiquidacion.NEXO:
            where.extend([Liquidacion.es_nexo.is_(True), Liquidacion.excluido_por_factura.is_(False)])
        elif segmento == SegmentoLiquidacion.GENERAL:
            where.extend([Liquidacion.es_nexo.is_(False), Liquidacion.excluido_por_factura.is_(False)])
        result = await self.session.execute(select(Liquidacion).where(*where).order_by(Liquidacion.created_at, Liquidacion.id))
        return list(result.scalars().all())

    async def exists_closed(self, *, cohorte_id: UUID, periodo: str) -> bool:
        result = await self.session.execute(
            select(Liquidacion.id)
            .where(
                Liquidacion.tenant_id == self.tenant_id,
                Liquidacion.deleted_at.is_(None),
                Liquidacion.cohorte_id == cohorte_id,
                Liquidacion.periodo == periodo,
                Liquidacion.estado == EstadoLiquidacion.CERRADA,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None


class FacturaRepository(TenantScopedRepository[Factura]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Factura, tenant_id)

    async def create(
        self, *, usuario_id: UUID, periodo: str, detalle: str, referencia_archivo: str, archivo_size_bytes: int
    ) -> Factura:
        record = Factura(
            tenant_id=self.tenant_id,
            usuario_id=usuario_id,
            periodo=periodo,
            detalle=detalle,
            referencia_archivo=referencia_archivo,
            archivo_size_bytes=archivo_size_bytes,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def update(
        self,
        record_id: UUID,
        *,
        periodo: str | None = None,
        detalle: str | None = None,
        referencia_archivo: str | None = None,
        archivo_size_bytes: int | None = None,
    ) -> Factura | None:
        record = await self.get(record_id)
        if record is None:
            return None
        if periodo is not None:
            record.periodo = periodo
        if detalle is not None:
            record.detalle = detalle
        if referencia_archivo is not None:
            record.referencia_archivo = referencia_archivo
        if archivo_size_bytes is not None:
            record.archivo_size_bytes = archivo_size_bytes
        return record

    async def mark_abonada(self, record_id: UUID, *, abonada_at: datetime | None = None) -> Factura | None:
        record = await self.get(record_id)
        if record is None:
            return None
        record.estado = EstadoFactura.ABONADA
        record.abonada_at = abonada_at or datetime.now(UTC)
        return record

    async def list_filtered(
        self,
        *,
        usuario_id: UUID | None = None,
        periodo: str | None = None,
        estado: EstadoFactura | None = None,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> list[Factura]:
        where = [Factura.tenant_id == self.tenant_id, Factura.deleted_at.is_(None)]
        if usuario_id is not None:
            where.append(Factura.usuario_id == usuario_id)
        if periodo is not None:
            where.append(Factura.periodo == periodo)
        if estado is not None:
            where.append(Factura.estado == estado)
        if desde is not None:
            where.append(cast(Factura.created_at, Date) >= desde)
        if hasta is not None:
            where.append(cast(Factura.created_at, Date) <= hasta)
        result = await self.session.execute(select(Factura).where(*where).order_by(Factura.created_at, Factura.id))
        return list(result.scalars().all())


class LiquidacionContextRepository:
    """Queries de contexto para servicios C-18, siempre acotadas por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id

    async def materia_exists(self, materia_id: UUID) -> bool:
        result = await self.session.execute(
            select(Materia.id)
            .where(Materia.id == materia_id, Materia.tenant_id == self.tenant_id, Materia.deleted_at.is_(None))
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def cohorte_exists(self, cohorte_id: UUID) -> bool:
        result = await self.session.execute(
            select(Cohorte.id)
            .where(Cohorte.id == cohorte_id, Cohorte.tenant_id == self.tenant_id, Cohorte.deleted_at.is_(None))
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def get_usuario(self, usuario_id: UUID) -> Usuario | None:
        result = await self.session.execute(
            select(Usuario).where(Usuario.id == usuario_id, Usuario.tenant_id == self.tenant_id, Usuario.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_usuarios_by_ids(self, usuario_ids: set[UUID]) -> dict[UUID, Usuario]:
        if not usuario_ids:
            return {}
        result = await self.session.execute(
            select(Usuario).where(
                Usuario.tenant_id == self.tenant_id,
                Usuario.deleted_at.is_(None),
                Usuario.id.in_(usuario_ids),
            )
        )
        return {usuario.id: usuario for usuario in result.scalars().all()}

    async def list_asignaciones_vigentes(self, *, cohorte_id: UUID, periodo: date) -> list[Asignacion]:
        result = await self.session.execute(
            select(Asignacion).where(
                Asignacion.tenant_id == self.tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.cohorte_id == cohorte_id,
                Asignacion.desde <= periodo,
                or_(Asignacion.hasta.is_(None), Asignacion.hasta >= periodo),
            )
        )
        return list(result.scalars().all())

    async def create_audit(
        self,
        *,
        actor_id: UUID,
        accion: str,
        detalle: dict,
        filas_afectadas: int,
    ) -> AuditLog:
        audit = AuditLog(
            tenant_id=self.tenant_id,
            actor_id=actor_id,
            accion=accion,
            detalle=detalle,
            filas_afectadas=filas_afectadas,
        )
        self.session.add(audit)
        await self.session.flush()
        return audit
