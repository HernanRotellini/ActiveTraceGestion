"""Modelos de usuarios y asignaciones del sistema."""

from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class Usuario(TenantScopedMixin, Base):
    __tablename__ = "usuarios"

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    email_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    dni: Mapped[str | None] = mapped_column(Text, nullable=True)
    cuil: Mapped[str | None] = mapped_column(Text, nullable=True)
    cbu: Mapped[str | None] = mapped_column(Text, nullable=True)
    alias_cbu: Mapped[str | None] = mapped_column(Text, nullable=True)
    telefono: Mapped[str | None] = mapped_column(Text, nullable=True)
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activo", server_default="activo")
    legajo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    banco: Mapped[str | None] = mapped_column(String(100), nullable=True)
    facturador: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")


class Asignacion(TenantScopedMixin, Base):
    __tablename__ = "asignaciones"

    usuario_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True)
    rol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    materia_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("materias.id"), nullable=True)
    carrera_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("carreras.id"), nullable=True)
    cohorte_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("cohortes.id"), nullable=True)
    comisiones: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    responsable_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True), nullable=True)
    desde: Mapped[date] = mapped_column(Date, nullable=False)
    hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
