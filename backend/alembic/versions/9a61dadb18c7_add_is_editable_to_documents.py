"""add_is_editable_to_documents

Revision ID: 9a61dadb18c7
Revises: 93b22cf9bc42
Create Date: 2026-07-17 00:51:22.918951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a61dadb18c7'
down_revision: Union[str, Sequence[str], None] = '93b22cf9bc42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'documents',
        sa.Column('is_editable', sa.Boolean(), server_default='0', nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('documents') as batch_op:
        batch_op.drop_column('is_editable')
