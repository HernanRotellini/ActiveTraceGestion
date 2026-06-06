"""comunicaciones — tabla comunicaciones + settings en tenant

Revision ID: 20260604_0008
Revises: 20260603_0007
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260604_0008"
down_revision: str | None = "20260603_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Add settings JSONB to tenants ──────────────────────────
    op.add_column(
        "tenants",
        sa.Column("settings", postgresql.JSONB, nullable=True, server_default=sa.text("'{}'::jsonb")),
    )

    # ── Create comunicaciones table ────────────────────────────
    op.create_table(
        "comunicaciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enviado_por_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("destinatario", sa.Text(), nullable=False),
        sa.Column("asunto", sa.String(length=255), nullable=False),
        sa.Column("cuerpo", sa.Text(), nullable=False),
        sa.Column(
            "estado",
            sa.Enum(
                "Pendiente", "Enviando", "Enviado", "Error", "Cancelado",
                name="estado_comunicacion",
                create_constraint=True,
            ),
            nullable=False,
            server_default="Pendiente",
        ),
        sa.Column("lote_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enviado_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["enviado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comunicaciones_tenant_id", "comunicaciones", ["tenant_id"])
    op.create_index("ix_comunicaciones_materia_id", "comunicaciones", ["materia_id"])
    op.create_index("ix_comunicaciones_lote_id", "comunicaciones", ["lote_id"])


def downgrade() -> None:
    op.drop_index("ix_comunicaciones_lote_id", table_name="comunicaciones")
    op.drop_index("ix_comunicaciones_materia_id", table_name="comunicaciones")
    op.drop_index("ix_comunicaciones_tenant_id", table_name="comunicaciones")
    op.drop_table("comunicaciones")
    op.execute("DROP TYPE IF EXISTS estado_comunicacion")
    op.drop_column("tenants", "settings")
