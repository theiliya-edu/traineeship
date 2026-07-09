"""Create table

Revision ID: a51ed10b6a4f
Revises:
Create Date: 2026-07-09 17:58:35.464085

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a51ed10b6a4f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('spimex_trading_results',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('exchange_product_id', sa.String(length=50), nullable=False),
                    sa.Column('exchange_product_name', sa.String(), nullable=False),
                    sa.Column('oil_id', sa.String(length=4), nullable=False),
                    sa.Column('delivery_basis_id', sa.String(length=3), nullable=False),
                    sa.Column('delivery_basis_name', sa.String(), nullable=False),
                    sa.Column('delivery_type_id', sa.String(length=1), nullable=False),
                    sa.Column('volume', sa.Integer(), nullable=True),
                    sa.Column('total', sa.Integer(), nullable=True),
                    sa.Column('count', sa.Integer(), nullable=True),
                    sa.Column('date', sa.Date(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('spimex_trading_results')
