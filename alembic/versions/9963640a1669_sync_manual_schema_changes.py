"""Sync manual schema changes

Revision ID: 9963640a1669
Revises: 3435109dc589
Create Date: 2024-02-12 15:11:24.513587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9963640a1669'
down_revision: Union[str, None] = '3435109dc589'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
