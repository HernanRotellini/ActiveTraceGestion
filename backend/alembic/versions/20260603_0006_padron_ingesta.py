"""padron ingesta — tablas version_padron y entrada_padron

Revision ID: 20260603_0006
Revises: 20260602_0005
Create Date: 2026-06-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260603_0006"
down_revision: str | None = "20260602_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "versiones_padron",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cargado_por", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cargado_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("activa", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohortes.id"]),
        sa.ForeignKeyConstraint(["cargado_por"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_versiones_padron_tenant_id", "versiones_padron", ["tenant_id"])
    op.create_index("ix_versiones_padron_materia_id", "versiones_padron", ["materia_id"])
    op.create_index("ix_versiones_padron_cohorte_id", "versiones_padron", ["cohorte_id"])
    op.create_index("ix_versiones_padron_activa", "versiones_padron", ["activa"])

    op.create_table(
        "entradas_padron",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellidos", sa.String(length=100), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("comision", sa.String(length=50), nullable=False),
        sa.Column("regional", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["version_id"], ["versiones_padron.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_entradas_padron_tenant_id", "entradas_padron", ["tenant_id"])
    op.create_index("ix_entradas_padron_version_id", "entradas_padron", ["version_id"])
    op.create_index("ix_entradas_padron_usuario_id", "entradas_padron", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_entradas_padron_usuario_id", table_name="entradas_padron")
    op.drop_index("ix_entradas_padron_version_id", table_name="entradas_padron")
    op.drop_index("ix_entradas_padron_tenant_id", table_name="entradas_padron")
    op.drop_table("entradas_padron")
    op.drop_index("ix_versiones_padron_activa", table_name="versiones_padron")
    op.drop_index("ix_versiones_padron_cohorte_id", table_name="versiones_padron")
    op.drop_index("ix_versiones_padron_materia_id", table_name="versiones_padron")
    op.drop_index("ix_versiones_padron_tenant_id", table_name="versiones_padron")
    op.drop_table("versiones_padron")
