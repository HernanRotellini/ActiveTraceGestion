"""c17 programas fechas — tablas programa_materia, fecha_academica

Revision ID: 20260607_0013
Revises: 20260607_0012
Create Date: 2026-06-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260607_0013"
down_revision: str | None = "20260607_0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    sa.Enum("Parcial", "TP", "Coloquio", "Recuperatorio", name="tipo_fecha_academica").create(op.get_bind())

    op.create_table(
        "programa_materia",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carrera_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("referencia_archivo", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.ForeignKeyConstraint(["carrera_id"], ["carreras.id"]),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohortes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_programa_materia_tenant_id", "programa_materia", ["tenant_id"])
    op.create_index("ix_programa_materia_materia_id", "programa_materia", ["materia_id"])
    op.create_index("ix_programa_materia_carrera_id", "programa_materia", ["carrera_id"])
    op.create_index("ix_programa_materia_cohorte_id", "programa_materia", ["cohorte_id"])
    op.create_index("ix_programa_tenant_materia", "programa_materia", ["tenant_id", "materia_id"])
    op.create_index("ix_programa_tenant_carrera", "programa_materia", ["tenant_id", "carrera_id"])
    op.create_index("ix_programa_tenant_cohorte", "programa_materia", ["tenant_id", "cohorte_id"])
    op.create_index("ix_programa_tenant_titulo", "programa_materia", ["tenant_id", "titulo"])
    op.create_index(
        "uq_programa_materia_tenant_contexto",
        "programa_materia",
        ["tenant_id", "materia_id", "carrera_id", "cohorte_id", "titulo"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "fecha_academica",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tipo", sa.Enum("Parcial", "TP", "Coloquio", "Recuperatorio", name="tipo_fecha_academica"), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("periodo", sa.String(length=50), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohortes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fecha_academica_tenant_id", "fecha_academica", ["tenant_id"])
    op.create_index("ix_fecha_academica_materia_id", "fecha_academica", ["materia_id"])
    op.create_index("ix_fecha_academica_cohorte_id", "fecha_academica", ["cohorte_id"])
    op.create_index("ix_fecha_tenant_materia", "fecha_academica", ["tenant_id", "materia_id"])
    op.create_index("ix_fecha_tenant_cohorte", "fecha_academica", ["tenant_id", "cohorte_id"])
    op.create_index("ix_fecha_tenant_tipo", "fecha_academica", ["tenant_id", "tipo"])
    op.create_index("ix_fecha_tenant_periodo", "fecha_academica", ["tenant_id", "periodo"])
    op.create_index("ix_fecha_tenant_materia_cohorte", "fecha_academica", ["tenant_id", "materia_id", "cohorte_id"])
    op.create_index("ix_fecha_fecha", "fecha_academica", ["tenant_id", "fecha"])
    op.create_index(
        "uq_fecha_academica_tenant_contexto",
        "fecha_academica",
        ["tenant_id", "materia_id", "cohorte_id", "tipo", "numero", "periodo"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_fecha_academica_tenant_contexto", table_name="fecha_academica")
    op.drop_index("ix_fecha_fecha", table_name="fecha_academica")
    op.drop_index("ix_fecha_tenant_materia_cohorte", table_name="fecha_academica")
    op.drop_index("ix_fecha_tenant_periodo", table_name="fecha_academica")
    op.drop_index("ix_fecha_tenant_tipo", table_name="fecha_academica")
    op.drop_index("ix_fecha_tenant_cohorte", table_name="fecha_academica")
    op.drop_index("ix_fecha_tenant_materia", table_name="fecha_academica")
    op.drop_index("ix_fecha_academica_cohorte_id", table_name="fecha_academica")
    op.drop_index("ix_fecha_academica_materia_id", table_name="fecha_academica")
    op.drop_index("ix_fecha_academica_tenant_id", table_name="fecha_academica")
    op.drop_table("fecha_academica")
    op.drop_index("uq_programa_materia_tenant_contexto", table_name="programa_materia")
    op.drop_index("ix_programa_tenant_titulo", table_name="programa_materia")
    op.drop_index("ix_programa_tenant_cohorte", table_name="programa_materia")
    op.drop_index("ix_programa_tenant_carrera", table_name="programa_materia")
    op.drop_index("ix_programa_tenant_materia", table_name="programa_materia")
    op.drop_index("ix_programa_materia_cohorte_id", table_name="programa_materia")
    op.drop_index("ix_programa_materia_carrera_id", table_name="programa_materia")
    op.drop_index("ix_programa_materia_materia_id", table_name="programa_materia")
    op.drop_index("ix_programa_materia_tenant_id", table_name="programa_materia")
    op.drop_table("programa_materia")
    op.execute("DROP TYPE IF EXISTS tipo_fecha_academica")
