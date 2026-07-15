"""Add foreign key indexes

Revision ID: 93b22cf9bc42
Revises: f8f213eee413
Create Date: 2026-07-14 02:22:00.000000

"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "93b22cf9bc42"
down_revision: str | Sequence[str] | None = "6fd5aed629a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: Add indexes on foreign key columns (handled by 6fd5aed629a7)."""
    pass


def downgrade() -> None:
    """Downgrade schema: Drop all added indexes (handled by 6fd5aed629a7)."""
    pass

