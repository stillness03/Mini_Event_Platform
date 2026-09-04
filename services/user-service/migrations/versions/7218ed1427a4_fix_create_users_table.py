"""fix_create_users_table

Revision ID: 7218ed1427a4
Revises: 5d68e863d775
Create Date: 2026-03-26 18:31:53.143661

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "7218ed1427a4"
down_revision: Union[str, Sequence[str], None] = "5d68e863d775"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
