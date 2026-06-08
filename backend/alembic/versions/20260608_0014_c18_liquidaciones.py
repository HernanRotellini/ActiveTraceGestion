"""c18 liquidaciones y honorarios — tablas salariales, liquidaciones y facturas

Revision ID: 20260608_0014
Revises: 20260607_0014
Create Date: 2026-06-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260608_0014"
down_revision: str | None = "20260607_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    sa.Enum("PROFESOR", "TUTOR", "NEXO", "COORDINADOR", name="rol_liquidacion").create(op.get_bind())
    sa.Enum("Abierta", "Cerrada", name="estado_liquidacion").create(op.get_bind())
    sa.Enum("Pendiente", "Abonada", name="estado_factura").create(op.get_bind())

    op.create_table(
        "salario_base",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rol", sa.Enum("PROFESOR", "TUTOR", "NEXO", "COORDINADOR", name="rol_liquidacion"), nullable=False),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_salario_base_tenant_id", "salario_base", ["tenant_id"])
    op.create_index("ix_salario_base_tenant_rol", "salario_base", ["tenant_id", "rol"])
    op.create_index("ix_salario_base_tenant_vigencia", "salario_base", ["tenant_id", "desde", "hasta"])
    op.create_index(
        "uq_salario_base_tenant_rol_vigencia_activo",
        "salario_base",
        ["tenant_id", "rol", "desde", "hasta"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "salario_plus",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rol", sa.Enum("PROFESOR", "TUTOR", "NEXO", "COORDINADOR", name="rol_liquidacion"), nullable=False),
        sa.Column("grupo", sa.String(length=50), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=False),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_salario_plus_tenant_id", "salario_plus", ["tenant_id"])
    op.create_index("ix_salario_plus_tenant_rol_grupo", "salario_plus", ["tenant_id", "rol", "grupo"])
    op.create_index("ix_salario_plus_tenant_vigencia", "salario_plus", ["tenant_id", "desde", "hasta"])
    op.create_index(
        "uq_salario_plus_tenant_rol_grupo_vigencia_activo",
        "salario_plus",
        ["tenant_id", "rol", "grupo", "desde", "hasta"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "materia_plus",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("grupo", sa.String(length=50), nullable=False),
        sa.Column("desde", sa.Date(), nullable=False),
        sa.Column("hasta", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_materia_plus_tenant_id", "materia_plus", ["tenant_id"])
    op.create_index("ix_materia_plus_materia_id", "materia_plus", ["materia_id"])
    op.create_index("ix_materia_plus_tenant_materia", "materia_plus", ["tenant_id", "materia_id"])
    op.create_index("ix_materia_plus_tenant_grupo", "materia_plus", ["tenant_id", "grupo"])
    op.create_index("ix_materia_plus_tenant_vigencia", "materia_plus", ["tenant_id", "desde", "hasta"])
    op.create_index(
        "uq_materia_plus_tenant_materia_vigencia_activo",
        "materia_plus",
        ["tenant_id", "materia_id", "desde", "hasta"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "liquidacion",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cohorte_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("periodo", sa.String(length=7), nullable=False),
        sa.Column("rol", sa.Enum("PROFESOR", "TUTOR", "NEXO", "COORDINADOR", name="rol_liquidacion"), nullable=False),
        sa.Column("estado", sa.Enum("Abierta", "Cerrada", name="estado_liquidacion"), server_default="Abierta", nullable=False),
        sa.Column("monto_base", sa.Numeric(12, 2), nullable=False),
        sa.Column("monto_plus", sa.Numeric(12, 2), nullable=False),
        sa.Column("monto_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("comisiones", postgresql.JSONB(), server_default="[]", nullable=False),
        sa.Column("es_nexo", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("excluido_por_factura", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["cohorte_id"], ["cohortes.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_liquidacion_tenant_id", "liquidacion", ["tenant_id"])
    op.create_index("ix_liquidacion_cohorte_id", "liquidacion", ["cohorte_id"])
    op.create_index("ix_liquidacion_usuario_id", "liquidacion", ["usuario_id"])
    op.create_index("ix_liquidacion_tenant_periodo", "liquidacion", ["tenant_id", "periodo"])
    op.create_index("ix_liquidacion_tenant_cohorte", "liquidacion", ["tenant_id", "cohorte_id"])
    op.create_index("ix_liquidacion_tenant_usuario", "liquidacion", ["tenant_id", "usuario_id"])
    op.create_index("ix_liquidacion_tenant_estado", "liquidacion", ["tenant_id", "estado"])
    op.create_index(
        "uq_liquidacion_cerrada_tenant_periodo_cohorte_usuario",
        "liquidacion",
        ["tenant_id", "periodo", "cohorte_id", "usuario_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND estado = 'Cerrada'"),
    )

    op.create_table(
        "factura",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("periodo", sa.String(length=7), nullable=False),
        sa.Column("detalle", sa.Text(), nullable=False),
        sa.Column("referencia_archivo", sa.String(length=500), nullable=False),
        sa.Column("archivo_size_bytes", sa.Integer(), nullable=False),
        sa.Column("estado", sa.Enum("Pendiente", "Abonada", name="estado_factura"), server_default="Pendiente", nullable=False),
        sa.Column("abonada_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_factura_tenant_id", "factura", ["tenant_id"])
    op.create_index("ix_factura_usuario_id", "factura", ["usuario_id"])
    op.create_index("ix_factura_tenant_usuario", "factura", ["tenant_id", "usuario_id"])
    op.create_index("ix_factura_tenant_periodo", "factura", ["tenant_id", "periodo"])
    op.create_index("ix_factura_tenant_estado", "factura", ["tenant_id", "estado"])
    op.create_index("ix_factura_tenant_periodo_estado", "factura", ["tenant_id", "periodo", "estado"])


def downgrade() -> None:
    op.drop_index("ix_factura_tenant_periodo_estado", table_name="factura")
    op.drop_index("ix_factura_tenant_estado", table_name="factura")
    op.drop_index("ix_factura_tenant_periodo", table_name="factura")
    op.drop_index("ix_factura_tenant_usuario", table_name="factura")
    op.drop_index("ix_factura_usuario_id", table_name="factura")
    op.drop_index("ix_factura_tenant_id", table_name="factura")
    op.drop_table("factura")
    op.drop_index("uq_liquidacion_cerrada_tenant_periodo_cohorte_usuario", table_name="liquidacion")
    op.drop_index("ix_liquidacion_tenant_estado", table_name="liquidacion")
    op.drop_index("ix_liquidacion_tenant_usuario", table_name="liquidacion")
    op.drop_index("ix_liquidacion_tenant_cohorte", table_name="liquidacion")
    op.drop_index("ix_liquidacion_tenant_periodo", table_name="liquidacion")
    op.drop_index("ix_liquidacion_usuario_id", table_name="liquidacion")
    op.drop_index("ix_liquidacion_cohorte_id", table_name="liquidacion")
    op.drop_index("ix_liquidacion_tenant_id", table_name="liquidacion")
    op.drop_table("liquidacion")
    op.drop_index("uq_materia_plus_tenant_materia_vigencia_activo", table_name="materia_plus")
    op.drop_index("ix_materia_plus_tenant_vigencia", table_name="materia_plus")
    op.drop_index("ix_materia_plus_tenant_grupo", table_name="materia_plus")
    op.drop_index("ix_materia_plus_tenant_materia", table_name="materia_plus")
    op.drop_index("ix_materia_plus_materia_id", table_name="materia_plus")
    op.drop_index("ix_materia_plus_tenant_id", table_name="materia_plus")
    op.drop_table("materia_plus")
    op.drop_index("uq_salario_plus_tenant_rol_grupo_vigencia_activo", table_name="salario_plus")
    op.drop_index("ix_salario_plus_tenant_vigencia", table_name="salario_plus")
    op.drop_index("ix_salario_plus_tenant_rol_grupo", table_name="salario_plus")
    op.drop_index("ix_salario_plus_tenant_id", table_name="salario_plus")
    op.drop_table("salario_plus")
    op.drop_index("uq_salario_base_tenant_rol_vigencia_activo", table_name="salario_base")
    op.drop_index("ix_salario_base_tenant_vigencia", table_name="salario_base")
    op.drop_index("ix_salario_base_tenant_rol", table_name="salario_base")
    op.drop_index("ix_salario_base_tenant_id", table_name="salario_base")
    op.drop_table("salario_base")
    op.execute("DROP TYPE IF EXISTS estado_factura")
    op.execute("DROP TYPE IF EXISTS estado_liquidacion")
    op.execute("DROP TYPE IF EXISTS rol_liquidacion")
