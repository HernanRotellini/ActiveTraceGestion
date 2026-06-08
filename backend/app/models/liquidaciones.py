"""Modelos ORM para liquidaciones y honorarios docentes."""

import enum
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class RolLiquidacion(str, enum.Enum):
    PROFESOR = "PROFESOR"
    TUTOR = "TUTOR"
    NEXO = "NEXO"
    COORDINADOR = "COORDINADOR"


class EstadoLiquidacion(str, enum.Enum):
    ABIERTA = "Abierta"
    CERRADA = "Cerrada"


class EstadoFactura(str, enum.Enum):
    PENDIENTE = "Pendiente"
    ABONADA = "Abonada"


class SegmentoLiquidacion(str, enum.Enum):
    GENERAL = "general"
    NEXO = "nexo"
    FACTURANTE = "facturante"


rol_liquidacion_enum = Enum(
    RolLiquidacion,
    name="rol_liquidacion",
    create_constraint=True,
    values_callable=lambda values: [item.value for item in values],
)
estado_liquidacion_enum = Enum(
    EstadoLiquidacion,
    name="estado_liquidacion",
    create_constraint=True,
    values_callable=lambda values: [item.value for item in values],
)
estado_factura_enum = Enum(
    EstadoFactura,
    name="estado_factura",
    create_constraint=True,
    values_callable=lambda values: [item.value for item in values],
)


class SalarioBase(TenantScopedMixin, Base):
    __tablename__ = "salario_base"

    rol: Mapped[RolLiquidacion] = mapped_column(rol_liquidacion_enum, nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    desde: Mapped[date] = mapped_column(Date, nullable=False)
    hasta: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        Index("ix_salario_base_tenant_rol", "tenant_id", "rol"),
        Index("ix_salario_base_tenant_vigencia", "tenant_id", "desde", "hasta"),
        Index(
            "uq_salario_base_tenant_rol_vigencia_activo",
            "tenant_id",
            "rol",
            "desde",
            "hasta",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


class SalarioPlus(TenantScopedMixin, Base):
    __tablename__ = "salario_plus"

    rol: Mapped[RolLiquidacion] = mapped_column(rol_liquidacion_enum, nullable=False)
    grupo: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    desde: Mapped[date] = mapped_column(Date, nullable=False)
    hasta: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        Index("ix_salario_plus_tenant_rol_grupo", "tenant_id", "rol", "grupo"),
        Index("ix_salario_plus_tenant_vigencia", "tenant_id", "desde", "hasta"),
        Index(
            "uq_salario_plus_tenant_rol_grupo_vigencia_activo",
            "tenant_id",
            "rol",
            "grupo",
            "desde",
            "hasta",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


class MateriaPlus(TenantScopedMixin, Base):
    __tablename__ = "materia_plus"

    materia_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("materias.id"), nullable=False, index=True)
    grupo: Mapped[str] = mapped_column(String(50), nullable=False)
    desde: Mapped[date] = mapped_column(Date, nullable=False)
    hasta: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        Index("ix_materia_plus_tenant_materia", "tenant_id", "materia_id"),
        Index("ix_materia_plus_tenant_grupo", "tenant_id", "grupo"),
        Index("ix_materia_plus_tenant_vigencia", "tenant_id", "desde", "hasta"),
        Index(
            "uq_materia_plus_tenant_materia_vigencia_activo",
            "tenant_id",
            "materia_id",
            "desde",
            "hasta",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


class Liquidacion(TenantScopedMixin, Base):
    __tablename__ = "liquidacion"

    cohorte_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("cohortes.id"), nullable=False, index=True)
    usuario_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    periodo: Mapped[str] = mapped_column(String(7), nullable=False)
    rol: Mapped[RolLiquidacion] = mapped_column(rol_liquidacion_enum, nullable=False)
    estado: Mapped[EstadoLiquidacion] = mapped_column(
        estado_liquidacion_enum,
        nullable=False,
        default=EstadoLiquidacion.ABIERTA,
        server_default=EstadoLiquidacion.ABIERTA.value,
    )
    monto_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    monto_plus: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    comisiones: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    es_nexo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    excluido_por_factura: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    __table_args__ = (
        Index("ix_liquidacion_tenant_periodo", "tenant_id", "periodo"),
        Index("ix_liquidacion_tenant_cohorte", "tenant_id", "cohorte_id"),
        Index("ix_liquidacion_tenant_usuario", "tenant_id", "usuario_id"),
        Index("ix_liquidacion_tenant_estado", "tenant_id", "estado"),
        Index(
            "uq_liquidacion_cerrada_tenant_periodo_cohorte_usuario",
            "tenant_id",
            "periodo",
            "cohorte_id",
            "usuario_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND estado = 'Cerrada'"),
        ),
    )


class Factura(TenantScopedMixin, Base):
    __tablename__ = "factura"

    usuario_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    periodo: Mapped[str] = mapped_column(String(7), nullable=False)
    detalle: Mapped[str] = mapped_column(Text, nullable=False)
    referencia_archivo: Mapped[str] = mapped_column(String(500), nullable=False)
    archivo_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[EstadoFactura] = mapped_column(
        estado_factura_enum,
        nullable=False,
        default=EstadoFactura.PENDIENTE,
        server_default=EstadoFactura.PENDIENTE.value,
    )
    abonada_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_factura_tenant_usuario", "tenant_id", "usuario_id"),
        Index("ix_factura_tenant_periodo", "tenant_id", "periodo"),
        Index("ix_factura_tenant_estado", "tenant_id", "estado"),
        Index("ix_factura_tenant_periodo_estado", "tenant_id", "periodo", "estado"),
    )
