"""enable pgvector extension

Revision ID: ec6ffc0dd32a
Revises: 8ed398b0a4d9
Create Date: 2026-07-04 00:51:48.596111

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ec6ffc0dd32a"
down_revision: Union[str, Sequence[str], None] = "8ed398b0a4d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS vector")
