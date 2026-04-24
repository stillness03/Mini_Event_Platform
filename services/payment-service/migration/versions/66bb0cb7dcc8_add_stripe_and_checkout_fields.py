"""add_stripe_and_checkout_fields

Revision ID: 66bb0cb7dcc8
Revises: 71a605b97918
Create Date: 2026-04-22 19:13:02.056275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66bb0cb7dcc8'
down_revision: Union[str, Sequence[str], None] = '71a605b97918'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('payments', sa.Column('stripe_id', sa.String(length=255), nullable=True))
    op.add_column('payments', sa.Column('checkout_url', sa.String(length=1024), nullable=True))
    op.create_index(op.f('ix_payments_stripe_id'), 'payments', ['stripe_id'], unique=True)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_payments_stripe_id'), table_name='payments')
    op.drop_column('payments', 'checkout_url')
    op.drop_column('payments', 'stripe_id')
    pass
