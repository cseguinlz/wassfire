"""Section back to varchar

Revision ID: e2f467e737ff
Revises: 9963640a1669
Create Date: 2024-02-12 16:00:18.764060

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e2f467e737ff"
down_revision: Union[str, None] = "9963640a1669"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Convert 'section' column from ENUM to VARCHAR
    op.alter_column(
        "products", "section", type_=sa.String(), postgresql_using="section::text"
    )


def downgrade():
    # Convert 'section' column back from VARCHAR to ENUM
    section_enum = sa.Enum(
        "men", "women", "kids", "sports", "collections", name="section_type"
    )
    section_enum.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "products",
        "section",
        type_=section_enum,
        postgresql_using="section::section_type",
    )
