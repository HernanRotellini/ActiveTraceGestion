"""encuentros_y_guardias — tablas slots_encuentro, instancias_encuentro, guardias

Revision ID: 20260604_0010
Revises: 20260604_0009
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260604_0010"
down_revision: str | None = "20260604_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Enum types ──────────────────────────────────────────────
    sa.Enum("Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", name="dia_semana").create(op.get_bind())
    sa.Enum("Programado", "Realizado", "Cancelado", name="estado_instancia").create(op.get_bind())
    sa.Enum("Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", name="dia_semana_guardia").create(op.get_bind())
    sa.Enum("Pendiente", "Realizada", "Cancelada", name="estado_guardia").create(op.get_bind())

    # ── SlotEncuentro ───────────────────────────────────────────
    op.create_table(
        "slots_encuentro",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asignacion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("dia_semana", sa.Enum("Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", name="dia_semana"), nullable=False),
        sa.Column("hora", sa.Time(), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("cant_semanas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fecha_unica", sa.Date(), nullable=True),
        sa.Column("meet_url", sa.Text(), nullable=True),
        sa.Column("vig_desde", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vig_hasta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["asignacion_id"], ["asignaciones.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_slots_encuentro_tenant_id", "slots_encuentro", ["tenant_id"])
    op.create_index("ix_slots_encuentro_asignacion_id", "slots_encuentro", ["asignacion_id"])
    op.create_index("ix_slots_encuentro_materia_id", "slots_encuentro", ["materia_id"])

    # ── InstanciaEncuentro ──────────────────────────────────────
    op.create_table(
        "instancias_encuentro",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora", sa.Time(), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("estado", sa.Enum("Programado", "Realizado", "Cancelado", name="estado_instancia"), nullable=False, server_default="Programado"),
        sa.Column("meet_url", sa.Text(), nullable=True),
        sa.Column("video_url", sa.Text(), nullable=True),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["slot_id"], ["slots_encuentro.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_instancias_encuentro_tenant_id", "instancias_encuentro", ["tenant_id"])
    op.create_index("ix_instancias_encuentro_slot_id", "instancias_encuentro", ["slot_id"])
    op.create_index("ix_instancias_encuentro_materia_id", "instancias_encuentro", ["materia_id"])
    op.create_index("ix_instancias_encuentro_fecha", "instancias_encuentro", ["fecha"])

    # ── Guardia ─────────────────────────────────────────────────
    op.create_table(
        "guardias",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asignacion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carrera_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dia", sa.Enum("Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", name="dia_semana_guardia"), nullable=False),
        sa.Column("horario", sa.String(length=50), nullable=False),
        sa.Column("estado", sa.Enum("Pendiente", "Realizada", "Cancelada", name="estado_guardia"), nullable=False, server_default="Pendiente"),
        sa.Column("comentarios", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["asignacion_id"], ["asignaciones.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.ForeignKeyConstraint(["carrera_id"], ["carreras.id"]),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohortes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_guardias_tenant_id", "guardias", ["tenant_id"])
    op.create_index("ix_guardias_asignacion_id", "guardias", ["asignacion_id"])
    op.create_index("ix_guardias_materia_id", "guardias", ["materia_id"])
    op.create_index("ix_guardias_carrera_id", "guardias", ["carrera_id"])
    op.create_index("ix_guardias_cohorte_id", "guardias", ["cohorte_id"])


def downgrade() -> None:
    op.drop_index("ix_guardias_cohorte_id", table_name="guardias")
    op.drop_index("ix_guardias_carrera_id", table_name="guardias")
    op.drop_index("ix_guardias_materia_id", table_name="guardias")
    op.drop_index("ix_guardias_asignacion_id", table_name="guardias")
    op.drop_index("ix_guardias_tenant_id", table_name="guardias")
    op.drop_table("guardias")
    op.drop_index("ix_instancias_encuentro_fecha", table_name="instancias_encuentro")
    op.drop_index("ix_instancias_encuentro_materia_id", table_name="instancias_encuentro")
    op.drop_index("ix_instancias_encuentro_slot_id", table_name="instancias_encuentro")
    op.drop_index("ix_instancias_encuentro_tenant_id", table_name="instancias_encuentro")
    op.drop_table("instancias_encuentro")
    op.drop_index("ix_slots_encuentro_materia_id", table_name="slots_encuentro")
    op.drop_index("ix_slots_encuentro_asignacion_id", table_name="slots_encuentro")
    op.drop_index("ix_slots_encuentro_tenant_id", table_name="slots_encuentro")
    op.drop_table("slots_encuentro")
    op.execute("DROP TYPE IF EXISTS dia_semana")
    op.execute("DROP TYPE IF EXISTS estado_instancia")
    op.execute("DROP TYPE IF EXISTS dia_semana_guardia")
    op.execute("DROP TYPE IF EXISTS estado_guardia")
