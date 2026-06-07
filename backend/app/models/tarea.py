"""Modelos de tareas internas y comentarios."""

import enum
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class EstadoTarea(str, enum.Enum):
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En progreso"
    RESUELTA = "Resuelta"
    CANCELADA = "Cancelada"


class Tarea(TenantScopedMixin, Base):
    __tablename__ = "tarea"

    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[EstadoTarea] = mapped_column(
        Enum(
            EstadoTarea,
            name="estado_tarea",
            create_constraint=True,
            values_callable=lambda values: [item.value for item in values],
        ),
        nullable=False,
        default=EstadoTarea.PENDIENTE,
        server_default=EstadoTarea.PENDIENTE.value,
    )
    asignado_a: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    asignado_por: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    materia_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("materias.id"), nullable=True, index=True
    )
    contexto_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True), nullable=True, index=True)

    __table_args__ = (
        Index("ix_tarea_tenant_asignado_estado", "tenant_id", "asignado_a", "estado"),
        Index("ix_tarea_tenant_asignador", "tenant_id", "asignado_por"),
        Index("ix_tarea_tenant_materia", "tenant_id", "materia_id"),
        Index("ix_tarea_tenant_estado", "tenant_id", "estado"),
        Index("ix_tarea_tenant_updated_at", "tenant_id", "updated_at"),
    )


class ComentarioTarea(TenantScopedMixin, Base):
    __tablename__ = "comentario_tarea"

    tarea_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("tarea.id"), nullable=False, index=True
    )
    autor_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    texto: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("ix_comentario_tarea_tenant_tarea_created", "tenant_id", "tarea_id", "created_at"),
    )
