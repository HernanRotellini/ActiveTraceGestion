"""Modelo ORM para hilos de mensajería interna."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantScopedMixin


class HiloMensaje(TenantScopedMixin, Base):
    __tablename__ = "hilos_mensajes"

    asunto: Mapped[str] = mapped_column(String(255), nullable=False)
    participantes_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    ultimo_mensaje_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    mensajes: Mapped[list[MensajeInterno]] = relationship(
        "MensajeInterno",
        back_populates="hilo",
        lazy="selectin",
        order_by="MensajeInterno.created_at",
    )
