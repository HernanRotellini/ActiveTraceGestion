"""evaluaciones_y_coloquios — tablas evaluacion, turno_evaluacion, reserva_evaluacion, resultado_evaluacion, convocatoria_alumno

Revision ID: 20260604_0009
Revises: 20260604_0008
Create Date: 2026-06-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260604_0009"
down_revision: str | None = "20260604_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Enum types ──────────────────────────────────────────────
    sa.Enum("Parcial", "TP", "Coloquio", "Recuperatorio", name="tipo_evaluacion").create(op.get_bind())
    sa.Enum("Activa", "Cerrada", name="estado_evaluacion").create(op.get_bind())
    sa.Enum("Activa", "Cancelada", name="estado_reserva").create(op.get_bind())

    # ── Evaluacion ──────────────────────────────────────────────
    op.create_table(
        "evaluaciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tipo", sa.Enum("Parcial", "TP", "Coloquio", "Recuperatorio", name="tipo_evaluacion"), nullable=False),
        sa.Column("instancia", sa.String(length=255), nullable=False),
        sa.Column("estado", sa.Enum("Activa", "Cerrada", name="estado_evaluacion"), nullable=False, server_default="Activa"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohortes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evaluaciones_tenant_id", "evaluaciones", ["tenant_id"])
    op.create_index("ix_evaluaciones_materia_id", "evaluaciones", ["materia_id"])
    op.create_index("ix_evaluaciones_cohorte_id", "evaluaciones", ["cohorte_id"])

    # ── TurnoEvaluacion ─────────────────────────────────────────
    op.create_table(
        "turnos_evaluacion",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evaluacion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=True),
        sa.Column("hora_fin", sa.Time(), nullable=True),
        sa.Column("cupo_maximo", sa.Integer(), nullable=False),
        sa.Column("cupo_restante", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluaciones.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_turnos_evaluacion_tenant_id", "turnos_evaluacion", ["tenant_id"])
    op.create_index("ix_turnos_evaluacion_evaluacion_id", "turnos_evaluacion", ["evaluacion_id"])

    # ── ReservaEvaluacion ───────────────────────────────────────
    op.create_table(
        "reservas_evaluacion",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evaluacion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("turno_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alumno_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("estado", sa.Enum("Activa", "Cancelada", name="estado_reserva"), nullable=False, server_default="Activa"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluaciones.id"]),
        sa.ForeignKeyConstraint(["turno_id"], ["turnos_evaluacion.id"]),
        sa.ForeignKeyConstraint(["alumno_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reservas_evaluacion_tenant_id", "reservas_evaluacion", ["tenant_id"])
    op.create_index("ix_reservas_evaluacion_evaluacion_id", "reservas_evaluacion", ["evaluacion_id"])
    op.create_index("ix_reservas_evaluacion_turno_id", "reservas_evaluacion", ["turno_id"])
    op.create_index("ix_reservas_evaluacion_alumno_id", "reservas_evaluacion", ["alumno_id"])
    op.create_index("ix_reservas_evaluacion_unique_activa", "reservas_evaluacion", ["evaluacion_id", "alumno_id"],
                    postgresql_where=sa.text("estado = 'Activa' AND deleted_at IS NULL"))

    # ── ResultadoEvaluacion ─────────────────────────────────────
    op.create_table(
        "resultados_evaluacion",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evaluacion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alumno_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nota_final", sa.Text(), nullable=False),
        sa.Column("registrado_por", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluaciones.id"]),
        sa.ForeignKeyConstraint(["alumno_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["registrado_por"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evaluacion_id", "alumno_id", name="uq_resultado_evaluacion_alumno"),
    )
    op.create_index("ix_resultados_evaluacion_tenant_id", "resultados_evaluacion", ["tenant_id"])
    op.create_index("ix_resultados_evaluacion_evaluacion_id", "resultados_evaluacion", ["evaluacion_id"])
    op.create_index("ix_resultados_evaluacion_alumno_id", "resultados_evaluacion", ["alumno_id"])

    # ── ConvocatoriaAlumno ──────────────────────────────────────
    op.create_table(
        "convocatorias_alumnos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evaluacion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alumno_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluaciones.id"]),
        sa.ForeignKeyConstraint(["alumno_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evaluacion_id", "alumno_id", name="uq_convocatoria_alumno"),
    )
    op.create_index("ix_convocatorias_alumnos_tenant_id", "convocatorias_alumnos", ["tenant_id"])
    op.create_index("ix_convocatorias_alumnos_evaluacion_id", "convocatorias_alumnos", ["evaluacion_id"])
    op.create_index("ix_convocatorias_alumnos_alumno_id", "convocatorias_alumnos", ["alumno_id"])


def downgrade() -> None:
    op.drop_index("ix_convocatorias_alumnos_alumno_id", table_name="convocatorias_alumnos")
    op.drop_index("ix_convocatorias_alumnos_evaluacion_id", table_name="convocatorias_alumnos")
    op.drop_index("ix_convocatorias_alumnos_tenant_id", table_name="convocatorias_alumnos")
    op.drop_table("convocatorias_alumnos")
    op.drop_index("ix_resultados_evaluacion_alumno_id", table_name="resultados_evaluacion")
    op.drop_index("ix_resultados_evaluacion_evaluacion_id", table_name="resultados_evaluacion")
    op.drop_index("ix_resultados_evaluacion_tenant_id", table_name="resultados_evaluacion")
    op.drop_table("resultados_evaluacion")
    op.drop_index("ix_reservas_evaluacion_unique_activa", table_name="reservas_evaluacion")
    op.drop_index("ix_reservas_evaluacion_alumno_id", table_name="reservas_evaluacion")
    op.drop_index("ix_reservas_evaluacion_turno_id", table_name="reservas_evaluacion")
    op.drop_index("ix_reservas_evaluacion_evaluacion_id", table_name="reservas_evaluacion")
    op.drop_index("ix_reservas_evaluacion_tenant_id", table_name="reservas_evaluacion")
    op.drop_table("reservas_evaluacion")
    op.drop_index("ix_turnos_evaluacion_evaluacion_id", table_name="turnos_evaluacion")
    op.drop_index("ix_turnos_evaluacion_tenant_id", table_name="turnos_evaluacion")
    op.drop_table("turnos_evaluacion")
    op.drop_index("ix_evaluaciones_cohorte_id", table_name="evaluaciones")
    op.drop_index("ix_evaluaciones_materia_id", table_name="evaluaciones")
    op.drop_index("ix_evaluaciones_tenant_id", table_name="evaluaciones")
    op.drop_table("evaluaciones")
    op.execute("DROP TYPE IF EXISTS tipo_evaluacion")
    op.execute("DROP TYPE IF EXISTS estado_evaluacion")
    op.execute("DROP TYPE IF EXISTS estado_reserva")
