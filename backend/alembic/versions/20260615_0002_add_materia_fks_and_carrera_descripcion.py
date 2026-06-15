"""add carrera_id, cohorte_id, carga_horaria to materias; add descripcion to carreras

Revision ID: 20260615_0002
Revises: 20260615_0001
Create Date: 2026-06-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260615_0002"
down_revision: str | None = "20260615_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("carreras", sa.Column("descripcion", sa.String(length=500), server_default="", nullable=False))
    op.add_column("materias", sa.Column("carrera_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_materias_carrera_id", "materias", "carreras", ["carrera_id"], ["id"])
    op.add_column("materias", sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_materias_cohorte_id", "materias", "cohortes", ["cohorte_id"], ["id"])
    op.add_column("materias", sa.Column("carga_horaria", sa.Integer(), server_default="0", nullable=False))
    op.create_index("ix_materias_carrera_id", "materias", ["carrera_id"])
    op.create_index("ix_materias_cohorte_id", "materias", ["cohorte_id"])


def downgrade() -> None:
    op.drop_index("ix_materias_cohorte_id", table_name="materias")
    op.drop_index("ix_materias_carrera_id", table_name="materias")
    op.drop_column("materias", "carga_horaria")
    op.drop_constraint("fk_materias_cohorte_id", "materias", type_="foreignkey")
    op.drop_column("materias", "cohorte_id")
    op.drop_constraint("fk_materias_carrera_id", "materias", type_="foreignkey")
    op.drop_column("materias", "carrera_id")
    op.drop_column("carreras", "descripcion")
