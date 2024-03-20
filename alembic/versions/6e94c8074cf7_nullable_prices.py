"""Nullable prices

Revision ID: 6e94c8074cf7
Revises: e2f467e737ff
Create Date: 2024-02-13 10:50:39.702517

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6e94c8074cf7"
down_revision: Union[str, None] = "e2f467e737ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "products", "discount_percentage", existing_type=sa.String(), nullable=True
    )
    op.alter_column(
        "products", "original_price", existing_type=sa.Float(), nullable=True
    )
    op.alter_column("products", "sale_price", existing_type=sa.Float(), nullable=True)


def downgrade() -> None:
    op.alter_column(
        "products", "discount_percentage", existing_type=sa.String(), nullable=False
    )  # Consider setting a default value if needed
    op.alter_column(
        "products", "original_price", existing_type=sa.Float(), nullable=False
    )  # Consider setting a default value if needed
    op.alter_column(
        "products", "sale_price", existing_type=sa.Float(), nullable=False
    )  # Consider setting a default value if needed
