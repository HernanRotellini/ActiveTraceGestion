"""Modelos del tablón de avisos institucionales y acknowledgment de lectura.

Implementa E13 del modelo de datos:
- Aviso: notificación con alcance, severidad, vigencia y requerimiento de ack
- AcknowledgmentAviso: confirmación de lectura por usuario
"""

import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class AlcanceAviso(str, enum.Enum):
    GLOBAL = "Global"
    POR_MATERIA = "PorMateria"
    POR_COHORTE = "PorCohorte"
    POR_ROL = "PorRol"


class SeveridadAviso(str, enum.Enum):
    INFO = "Info"
    ADVERTENCIA = "Advertencia"
    CRITICO = "Critico"


class Aviso(TenantScopedMixin, Base):
    __tablename__ = "avisos"

    alcance: Mapped[AlcanceAviso] = mapped_column(
        Enum(AlcanceAviso, name="alcance_aviso", create_constraint=True),
        nullable=False,
        index=True,
    )
    materia_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("materias.id"),
        nullable=True,
        index=True,
    )
    cohorte_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("cohortes.id"),
        nullable=True,
        index=True,
    )
    rol_destino: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    severidad: Mapped[SeveridadAviso] = mapped_column(
        Enum(SeveridadAviso, name="severidad_aviso", create_constraint=True),
        nullable=False,
        default=SeveridadAviso.INFO,
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    inicio_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    fin_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requiere_ack: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Índice compuesto para filtrado por visibilidad
    __table_args__ = (
        # Índice para query de visibilidad: tenant + activo + inicio_en + alcance
        # Definido en migración, no como decorador
    )


class AcknowledgmentAviso(TenantScopedMixin, Base):
    __tablename__ = "acknowledgments_aviso"

    aviso_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("avisos.id"),
        nullable=False,
        index=True,
    )
    usuario_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )
    confirmado_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("aviso_id", "usuario_id", name="uq_aviso_usuario_ack"),
    )
