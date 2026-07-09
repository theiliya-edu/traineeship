"""Change 'total' to BigInteger

Revision ID: d72077b7dae9
Revises: 52d31e93e59e
Create Date: 2026-07-14 18:36:44.260489

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd72077b7dae9'
down_revision: Union[str, Sequence[str], None] = '52d31e93e59e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('spimex_trading_results', 'total',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('spimex_trading_results', 'total',
                    existing_type=sa.BigInteger(),
                    type_=sa.INTEGER(),
                    existing_nullable=True)
