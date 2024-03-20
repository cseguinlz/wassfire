"""Adding new Adidas fields, published date, 2nd image and type

Revision ID: d81d7a5f1385
Revises: 788d485bf931
Create Date: 2024-02-14 12:41:06.170705

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d81d7a5f1385"
down_revision: Union[str, None] = "788d485bf931"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename column color_variations to color
    op.alter_column("products", "color_variations", new_column_name="color")

    # Add new columns
    op.add_column("products", sa.Column("type", sa.String(), nullable=True))
    op.add_column(
        "products", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("products", sa.Column("second_image_url", sa.String(), nullable=True))


def downgrade() -> None:
    # Rename column color back to color_variations
    op.alter_column("products", "color", new_column_name="color_variations")

    # Remove added columns
    op.drop_column("products", "type")
    op.drop_column("products", "published_at")
    op.drop_column("products", "second_image_url")
