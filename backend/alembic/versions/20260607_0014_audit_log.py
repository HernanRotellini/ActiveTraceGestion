"""c05 audit log — tabla audit_log append-only con triggers

Revision ID: 20260607_0014
Revises: 20260607_0013
Create Date: 2026-06-07
"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa

revision: str = "20260607_0014"
down_revision: str | None = "20260607_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("impersonado_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("materia_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("accion", sa.String(length=100), nullable=False),
        sa.Column("detalle", postgresql.JSONB, nullable=True),
        sa.Column("filas_afectadas", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["actor_id"], ["auth_users.id"]),
        sa.ForeignKeyConstraint(["impersonado_id"], ["auth_users.id"]),
        sa.ForeignKeyConstraint(["materia_id"], ["materias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_log_tenant_id", "audit_log", ["tenant_id"])
    op.create_index("ix_audit_log_actor_id", "audit_log", ["actor_id"])
    op.create_index("ix_audit_log_accion", "audit_log", ["accion"])
    op.create_index("ix_audit_log_fecha_hora", "audit_log", ["fecha_hora"])
    op.create_index("ix_audit_log_tenant_fecha", "audit_log", ["tenant_id", "fecha_hora"])

    op.execute(
        """
        CREATE OR REPLACE FUNCTION reject_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only: modifications are not allowed';
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER audit_log_append_only_before_update
            BEFORE UPDATE ON audit_log
            FOR EACH ROW
            EXECUTE FUNCTION reject_audit_log_modification();
        """
    )

    op.execute(
        """
        CREATE TRIGGER audit_log_append_only_before_delete
            BEFORE DELETE ON audit_log
            FOR EACH ROW
            EXECUTE FUNCTION reject_audit_log_modification();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS audit_log_append_only_before_update ON audit_log")
    op.execute("DROP TRIGGER IF EXISTS audit_log_append_only_before_delete ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS reject_audit_log_modification()")
    op.drop_index("ix_audit_log_tenant_fecha", table_name="audit_log")
    op.drop_index("ix_audit_log_fecha_hora", table_name="audit_log")
    op.drop_index("ix_audit_log_accion", table_name="audit_log")
    op.drop_index("ix_audit_log_actor_id", table_name="audit_log")
    op.drop_index("ix_audit_log_tenant_id", table_name="audit_log")
    op.drop_table("audit_log")
