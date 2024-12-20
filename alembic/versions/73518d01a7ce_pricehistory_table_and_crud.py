"""PriceHistory table and CRUD

Revision ID: 73518d01a7ce
Revises: e528005b0a4e
Create Date: 2024-03-31 16:39:16.548948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73518d01a7ce'
down_revision: Union[str, None] = 'e528005b0a4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('price_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('discount_percentage', sa.Float(), nullable=True),
    sa.Column('original_price', sa.Float(), nullable=True),
    sa.Column('sale_price', sa.Float(), nullable=True),
    sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name=op.f('price_history_product_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('price_history_pkey'))
    )
    op.create_index(op.f('price_history_id_idx'), 'price_history', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('price_history_id_idx'), table_name='price_history')
    op.drop_table('price_history')
    # ### end Alembic commands ###
