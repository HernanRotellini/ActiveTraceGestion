"""usuarios y asignaciones — tabla de usuarios con PII cifrada y asignaciones

Revision ID: 20260602_0005
Revises: 20260602_0004
Create Date: 2026-06-02
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260602_0005"
down_revision: str | None = "20260602_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellidos", sa.String(length=100), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("email_hash", sa.String(length=64), nullable=True),
        sa.Column("dni", sa.Text(), nullable=True),
        sa.Column("cuil", sa.Text(), nullable=True),
        sa.Column("cbu", sa.Text(), nullable=True),
        sa.Column("alias_cbu", sa.Text(), nullable=True),
        sa.Column("telefono", sa.Text(), nullable=True),
        sa.Column("direccion", sa.Text(), nullable=True),
        sa.Column("estado", sa.String(length=20), server_default="activo", nullable=False),
        sa.Column("legajo", sa.String(length=50), nullable=True),
        sa.Column("banco", sa.String(length=100), nullable=True),
        sa.Column("facturador", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_tenant_id", "usuarios", ["tenant_id"])
    op.create_index("ix_usuarios_email_hash", "usuarios", ["email_hash"])

    op.create_table(
        "asignaciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rol", sa.String(length=50), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("carrera_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("comisiones", postgresql.JSONB(), nullable=True),
        sa.Column("responsable_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.ForeignKeyConstraint(["carrera_id"], ["carreras.id"]),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohortes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_asignaciones_tenant_id", "asignaciones", ["tenant_id"])
    op.create_index("ix_asignaciones_usuario_id", "asignaciones", ["usuario_id"])
    op.create_index("ix_asignaciones_materia_id", "asignaciones", ["materia_id"])
    op.create_index("ix_asignaciones_rol", "asignaciones", ["rol"])


def downgrade() -> None:
    op.drop_index("ix_asignaciones_rol", table_name="asignaciones")
    op.drop_index("ix_asignaciones_materia_id", table_name="asignaciones")
    op.drop_index("ix_asignaciones_usuario_id", table_name="asignaciones")
    op.drop_index("ix_asignaciones_tenant_id", table_name="asignaciones")
    op.drop_table("asignaciones")
    op.drop_index("ix_usuarios_email_hash", table_name="usuarios")
    op.drop_index("ix_usuarios_tenant_id", table_name="usuarios")
    op.drop_table("usuarios")
