"""add executions status check

Revision ID: b7c1e4f2a9d3
Revises: 177bc815251e
Create Date: 2026-11-06 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7c1e4f2a9d3"
down_revision: str | Sequence[str] | None = "177bc815251e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Añadir la restricción de estados permitidos."""
    op.create_check_constraint(
        "ck_executions_status",
        "executions",
        "status IN ('pending', 'running', 'completed', 'failed', 'cancelled')",
    )


def downgrade() -> None:
    """Eliminar la restricción de estados permitidos."""
    op.drop_constraint("ck_executions_status", "executions", type_="check")
