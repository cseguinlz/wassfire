"""fix(model): Made image_url required

Revision ID: 6d476bbd9643
Revises: 73518d01a7ce
Create Date: 2024-04-06 13:50:07.181325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d476bbd9643'
down_revision: Union[str, None] = '73518d01a7ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'image_url',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'image_url',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
