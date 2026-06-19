"""add periodo_id to fecha_academica

Revision ID: 20260618_0003
Revises: 20260618_0002
Create Date: 2026-06-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260618_0003"
down_revision: str | None = "20260618_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "fecha_academica",
        sa.Column("periodo_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_fecha_academica_periodo_id", "fecha_academica", ["periodo_id"])
    op.create_index(
        "ix_fecha_tenant_periodo_id",
        "fecha_academica",
        ["tenant_id", "periodo_id"],
    )
    op.create_foreign_key(
        "fk_fecha_academica_periodo_id",
        "fecha_academica",
        "periodos_academicos",
        ["periodo_id"],
        ["id"],
    )

    op.execute(
        """
        UPDATE fecha_academica fa
        SET periodo_id = pa.id
        FROM periodos_academicos pa
        WHERE fa.periodo_id IS NULL
          AND fa.tenant_id = pa.tenant_id
          AND fa.deleted_at IS NULL
          AND pa.deleted_at IS NULL
          AND fa.fecha BETWEEN pa.fecha_inicio AND pa.fecha_fin
        """
    )


def downgrade() -> None:
    op.drop_constraint("fk_fecha_academica_periodo_id", "fecha_academica", type_="foreignkey")
    op.drop_index("ix_fecha_tenant_periodo_id", table_name="fecha_academica")
    op.drop_index("ix_fecha_academica_periodo_id", table_name="fecha_academica")
    op.drop_column("fecha_academica", "periodo_id")
