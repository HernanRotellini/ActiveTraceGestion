"""Schemas Pydantic para liquidaciones y honorarios."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.liquidaciones import EstadoFactura, EstadoLiquidacion, RolLiquidacion, SegmentoLiquidacion


PERIODO_PATTERN = r"^\d{4}-\d{2}$"


class SalarioBaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rol: RolLiquidacion
    monto: Decimal = Field(..., gt=Decimal("0"), max_digits=12, decimal_places=2)
    desde: date
    hasta: date | None = None


class SalarioBaseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rol: RolLiquidacion | None = None
    monto: Decimal | None = Field(default=None, gt=Decimal("0"), max_digits=12, decimal_places=2)
    desde: date | None = None
    hasta: date | None = None


class SalarioBaseResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    rol: RolLiquidacion
    monto: Decimal
    desde: date
    hasta: date | None
    created_at: datetime


class SalarioPlusCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rol: RolLiquidacion
    grupo: str = Field(..., max_length=50)
    descripcion: str = Field(..., max_length=255)
    monto: Decimal = Field(..., gt=Decimal("0"), max_digits=12, decimal_places=2)
    desde: date
    hasta: date | None = None


class SalarioPlusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    rol: RolLiquidacion
    grupo: str
    descripcion: str
    monto: Decimal
    desde: date
    hasta: date | None
    created_at: datetime


class MateriaPlusCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    grupo: str = Field(..., max_length=50)
    desde: date
    hasta: date | None = None


class MateriaPlusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    materia_id: UUID
    grupo: str
    desde: date
    hasta: date | None
    created_at: datetime


class LiquidacionPreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cohorte_id: UUID
    periodo: str = Field(..., pattern=PERIODO_PATTERN)


class LiquidacionPreviewItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    usuario_id: UUID
    rol: RolLiquidacion
    monto_base: Decimal
    monto_plus: Decimal
    monto_total: Decimal
    comisiones: list[str]
    es_nexo: bool
    excluido_por_factura: bool
    procesable: bool
    motivo_no_procesable: str | None


class LiquidacionPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    cohorte_id: UUID
    periodo: str
    items: list[LiquidacionPreviewItemResponse]
    total_pagable: Decimal
    segmento_nexo_total: Decimal
    segmento_facturantes_total: Decimal


class LiquidacionCloseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cohorte_id: UUID
    periodo: str = Field(..., pattern=PERIODO_PATTERN)


class LiquidacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    cohorte_id: UUID
    usuario_id: UUID
    periodo: str
    rol: RolLiquidacion
    estado: EstadoLiquidacion
    monto_base: Decimal
    monto_plus: Decimal
    monto_total: Decimal
    comisiones: list[str]
    es_nexo: bool
    excluido_por_factura: bool
    created_at: datetime


class FacturaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usuario_id: UUID
    periodo: str = Field(..., pattern=PERIODO_PATTERN)
    detalle: str = Field(..., min_length=1)
    referencia_archivo: str = Field(..., max_length=500)
    archivo_size_bytes: int = Field(..., gt=0)


class FacturaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    periodo: str | None = Field(default=None, pattern=PERIODO_PATTERN)
    detalle: str | None = Field(default=None, min_length=1)
    referencia_archivo: str | None = Field(default=None, max_length=500)
    archivo_size_bytes: int | None = Field(default=None, gt=0)


class FacturaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    usuario_id: UUID
    periodo: str
    detalle: str
    referencia_archivo: str
    archivo_size_bytes: int
    estado: EstadoFactura
    abonada_at: datetime | None
    created_at: datetime
