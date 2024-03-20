"""Product link as unique identifier

Revision ID: 788d485bf931
Revises: 6e94c8074cf7
Create Date: 2024-02-13 14:34:40.180149

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "788d485bf931"
down_revision: Union[str, None] = "6e94c8074cf7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # op.alter_column("products", "product_link", existing_type=sa.String(), unique=True)
    # Use `create_unique_constraint` to add a unique constraint to `product_link`
    op.create_unique_constraint(
        "uq_products_product_link", "products", ["product_link"]
    )


def downgrade() -> None:
    # op.alter_column("products", "product_link", existing_type=sa.String(), unique=False)
    # Use `drop_constraint` to remove the unique constraint from `product_link`
    op.drop_constraint("uq_products_product_link", "products", type_="unique")
