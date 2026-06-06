"""calificaciones y umbral — tablas calificacion y umbral_materia

Revision ID: 20260603_0007
Revises: 20260603_0006
Create Date: 2026-06-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260603_0007"
down_revision: str | None = "20260603_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "calificaciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entrada_padron_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actividad", sa.String(length=255), nullable=False),
        sa.Column("nota_numerica", sa.Float(), nullable=True),
        sa.Column("nota_textual", sa.String(length=255), nullable=True),
        sa.Column("aprobado", sa.Boolean(), nullable=False),
        sa.Column(
            "origen",
            sa.Enum("Importado", "Manual", name="origen_calificacion", create_constraint=True),
            nullable=False,
        ),
        sa.Column("importado_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["entrada_padron_id"], ["entradas_padron.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "materia_id", "entrada_padron_id", "actividad",
            name="uq_calificacion_actividad",
        ),
    )
    op.create_index("ix_calificaciones_tenant_id", "calificaciones", ["tenant_id"])
    op.create_index("ix_calificaciones_materia_id", "calificaciones", ["materia_id"])
    op.create_index("ix_calificaciones_entrada_padron_id", "calificaciones", ["entrada_padron_id"])

    op.create_table(
        "umbrales_materia",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asignacion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("umbral_pct", sa.Integer(), nullable=False, server_default=sa.text("60")),
        sa.Column("valores_aprobatorios", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["asignacion_id"], ["asignaciones.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "asignacion_id", "materia_id",
            name="uq_umbral_asignacion_materia",
        ),
    )
    op.create_index("ix_umbrales_materia_tenant_id", "umbrales_materia", ["tenant_id"])
    op.create_index("ix_umbrales_materia_asignacion_id", "umbrales_materia", ["asignacion_id"])
    op.create_index("ix_umbrales_materia_materia_id", "umbrales_materia", ["materia_id"])


def downgrade() -> None:
    op.drop_index("ix_umbrales_materia_materia_id", table_name="umbrales_materia")
    op.drop_index("ix_umbrales_materia_asignacion_id", table_name="umbrales_materia")
    op.drop_index("ix_umbrales_materia_tenant_id", table_name="umbrales_materia")
    op.drop_table("umbrales_materia")

    op.drop_index("ix_calificaciones_entrada_padron_id", table_name="calificaciones")
    op.drop_index("ix_calificaciones_materia_id", table_name="calificaciones")
    op.drop_index("ix_calificaciones_tenant_id", table_name="calificaciones")
    op.drop_table("calificaciones")

    op.execute("DROP TYPE IF EXISTS origen_calificacion")
