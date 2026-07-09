"""Create table

Revision ID: 52d31e93e59e
Revises:
Create Date: 2026-07-14 15:47:57.790560

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '52d31e93e59e'
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
    op.create_index(op.f('ix_spimex_trading_results_date'), 'spimex_trading_results', ['date'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_spimex_trading_results_date'), table_name='spimex_trading_results')
    op.drop_table('spimex_trading_results')
