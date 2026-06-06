"""avisos_acknowledgment — tablas avisos, acknowledgments_aviso

Revision ID: 20260606_0011
Revises: 20260604_0010
Create Date: 2026-06-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260606_0011"
down_revision: str | None = "20260604_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Enum types ──────────────────────────────────────────────
    sa.Enum("Global", "PorMateria", "PorCohorte", "PorRol", name="alcance_aviso").create(op.get_bind())
    sa.Enum("Info", "Advertencia", "Critico", name="severidad_aviso").create(op.get_bind())

    # ── Aviso ────────────────────────────────────────────────────
    op.create_table(
        "avisos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alcance", sa.Enum("Global", "PorMateria", "PorCohorte", "PorRol", name="alcance_aviso"), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rol_destino", sa.String(length=50), nullable=True),
        sa.Column("severidad", sa.Enum("Info", "Advertencia", "Critico", name="severidad_aviso"), nullable=False, server_default="Info"),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("cuerpo", sa.Text(), nullable=False),
        sa.Column("inicio_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fin_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("requiere_ack", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohortes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_avisos_tenant_id", "avisos", ["tenant_id"])
    op.create_index("ix_avisos_alcance", "avisos", ["alcance"])
    op.create_index("ix_avisos_materia_id", "avisos", ["materia_id"])
    op.create_index("ix_avisos_cohorte_id", "avisos", ["cohorte_id"])
    op.create_index("ix_avisos_rol_destino", "avisos", ["rol_destino"])
    op.create_index("ix_avisos_inicio_en", "avisos", ["inicio_en"])
    # Índice compuesto para query de visibilidad: tenant + activo + inicio_en + alcance
    op.create_index(
        "ix_avisos_visibilidad",
        "avisos",
        ["tenant_id", "activo", "inicio_en", "alcance"],
        postgresql_using="btree",
    )

    # ── AcknowledgmentAviso ──────────────────────────────────────
    op.create_table(
        "acknowledgments_aviso",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aviso_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("confirmado_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["aviso_id"], ["avisos.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("aviso_id", "usuario_id", name="uq_aviso_usuario_ack"),
    )
    op.create_index("ix_acknowledgments_aviso_tenant_id", "acknowledgments_aviso", ["tenant_id"])
    op.create_index("ix_acknowledgments_aviso_aviso_id", "acknowledgments_aviso", ["aviso_id"])
    op.create_index("ix_acknowledgments_aviso_usuario_id", "acknowledgments_aviso", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_acknowledgments_aviso_usuario_id", table_name="acknowledgments_aviso")
    op.drop_index("ix_acknowledgments_aviso_aviso_id", table_name="acknowledgments_aviso")
    op.drop_index("ix_acknowledgments_aviso_tenant_id", table_name="acknowledgments_aviso")
    op.drop_table("acknowledgments_aviso")
    op.drop_index("ix_avisos_visibilidad", table_name="avisos")
    op.drop_index("ix_avisos_inicio_en", table_name="avisos")
    op.drop_index("ix_avisos_rol_destino", table_name="avisos")
    op.drop_index("ix_avisos_cohorte_id", table_name="avisos")
    op.drop_index("ix_avisos_materia_id", table_name="avisos")
    op.drop_index("ix_avisos_alcance", table_name="avisos")
    op.drop_index("ix_avisos_tenant_id", table_name="avisos")
    op.drop_table("avisos")
    op.execute("DROP TYPE IF EXISTS alcance_aviso")
    op.execute("DROP TYPE IF EXISTS severidad_aviso")
