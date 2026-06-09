"""tareas_internas — tablas tarea, comentario_tarea

Revision ID: 20260607_0012
Revises: 20260606_0011
Create Date: 2026-06-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260607_0012"
down_revision: str | None = "20260606_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    estado_tarea = postgresql.ENUM(
        "Pendiente", "En progreso", "Resuelta", "Cancelada", name="estado_tarea", create_type=False
    )
    estado_tarea.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tarea",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("estado", estado_tarea, server_default="Pendiente", nullable=False),
        sa.Column("asignado_a", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asignado_por", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contexto_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["asignado_a"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["asignado_por"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tarea_tenant_id", "tarea", ["tenant_id"])
    op.create_index("ix_tarea_asignado_a", "tarea", ["asignado_a"])
    op.create_index("ix_tarea_asignado_por", "tarea", ["asignado_por"])
    op.create_index("ix_tarea_materia_id", "tarea", ["materia_id"])
    op.create_index("ix_tarea_contexto_id", "tarea", ["contexto_id"])
    op.create_index("ix_tarea_tenant_asignado_estado", "tarea", ["tenant_id", "asignado_a", "estado"])
    op.create_index("ix_tarea_tenant_asignador", "tarea", ["tenant_id", "asignado_por"])
    op.create_index("ix_tarea_tenant_materia", "tarea", ["tenant_id", "materia_id"])
    op.create_index("ix_tarea_tenant_estado", "tarea", ["tenant_id", "estado"])
    op.create_index("ix_tarea_tenant_updated_at", "tarea", ["tenant_id", "updated_at"])

    op.create_table(
        "comentario_tarea",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tarea_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("autor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["tarea_id"], ["tarea.id"]),
        sa.ForeignKeyConstraint(["autor_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comentario_tarea_tenant_id", "comentario_tarea", ["tenant_id"])
    op.create_index("ix_comentario_tarea_tarea_id", "comentario_tarea", ["tarea_id"])
    op.create_index("ix_comentario_tarea_autor_id", "comentario_tarea", ["autor_id"])
    op.create_index("ix_comentario_tarea_tenant_tarea_created", "comentario_tarea", ["tenant_id", "tarea_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_comentario_tarea_tenant_tarea_created", table_name="comentario_tarea")
    op.drop_index("ix_comentario_tarea_autor_id", table_name="comentario_tarea")
    op.drop_index("ix_comentario_tarea_tarea_id", table_name="comentario_tarea")
    op.drop_index("ix_comentario_tarea_tenant_id", table_name="comentario_tarea")
    op.drop_table("comentario_tarea")
    op.drop_index("ix_tarea_tenant_updated_at", table_name="tarea")
    op.drop_index("ix_tarea_tenant_estado", table_name="tarea")
    op.drop_index("ix_tarea_tenant_materia", table_name="tarea")
    op.drop_index("ix_tarea_tenant_asignador", table_name="tarea")
    op.drop_index("ix_tarea_tenant_asignado_estado", table_name="tarea")
    op.drop_index("ix_tarea_contexto_id", table_name="tarea")
    op.drop_index("ix_tarea_materia_id", table_name="tarea")
    op.drop_index("ix_tarea_asignado_por", table_name="tarea")
    op.drop_index("ix_tarea_asignado_a", table_name="tarea")
    op.drop_index("ix_tarea_tenant_id", table_name="tarea")
    op.drop_table("tarea")
    op.execute("DROP TYPE IF EXISTS estado_tarea")
