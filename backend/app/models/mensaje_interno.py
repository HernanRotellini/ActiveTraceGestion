"""Modelo ORM para mensajes dentro de un hilo."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import UuidPrimaryKeyMixin


class MensajeInterno(UuidPrimaryKeyMixin, Base):
    __tablename__ = "mensajes_internos"

    hilo_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("hilos_mensajes.id"),
        nullable=False,
        index=True,
    )
    remitente_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
    )
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    hilo: Mapped[HiloMensaje] = relationship(
        "HiloMensaje",
        back_populates="mensajes",
    )
