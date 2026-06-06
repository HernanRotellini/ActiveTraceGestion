"""Modelo de comunicación con máquina de estados y cifrado en destinatario."""

import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class EstadoComunicacion(str, enum.Enum):
    PENDIENTE = "Pendiente"
    ENVIANDO = "Enviando"
    ENVIADO = "Enviado"
    ERROR = "Error"
    CANCELADO = "Cancelado"


_TRANSICIONES_VALIDAS: dict[EstadoComunicacion, set[EstadoComunicacion]] = {
    EstadoComunicacion.PENDIENTE: {EstadoComunicacion.ENVIANDO, EstadoComunicacion.CANCELADO},
    EstadoComunicacion.ENVIANDO: {EstadoComunicacion.ENVIADO, EstadoComunicacion.ERROR},
    EstadoComunicacion.ENVIADO: set(),
    EstadoComunicacion.ERROR: set(),
    EstadoComunicacion.CANCELADO: set(),
}


def validar_transicion(actual: EstadoComunicacion, nuevo: EstadoComunicacion) -> None:
    """Valida que la transición de estado sea permitida (RN-15)."""
    permitidos = _TRANSICIONES_VALIDAS.get(actual, set())
    if nuevo not in permitidos:
        raise ValueError(
            f"Transición inválida: {actual.value} → {nuevo.value}. "
            f"Transiciones permitidas desde {actual.value}: "
            f"{' ,'.join(e.value for e in permitidos) or 'ninguna'}."
        )


class Comunicacion(TenantScopedMixin, Base):
    __tablename__ = "comunicaciones"

    enviado_por_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
    )
    materia_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("materias.id"),
        nullable=False,
        index=True,
    )
    destinatario: Mapped[str] = mapped_column(Text, nullable=False)
    asunto: Mapped[str] = mapped_column(String(255), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[EstadoComunicacion] = mapped_column(
        Enum(EstadoComunicacion, name="estado_comunicacion", create_constraint=True),
        nullable=False,
        default=EstadoComunicacion.PENDIENTE,
    )
    lote_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        nullable=False,
        index=True,
        default=uuid4,
    )
    enviado_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def transicionar(self, nuevo_estado: EstadoComunicacion) -> None:
        """Aplica una transición de estado con validación (RN-15)."""
        validar_transicion(self.estado, nuevo_estado)
        self.estado = nuevo_estado
