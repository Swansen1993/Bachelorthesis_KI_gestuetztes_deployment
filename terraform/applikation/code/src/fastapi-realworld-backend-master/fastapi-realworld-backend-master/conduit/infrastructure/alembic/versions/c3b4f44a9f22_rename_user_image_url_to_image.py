"""rename user image_url to image

Revision ID: c3b4f44a9f22
Revises: 666cc53a93be
Create Date: 2026-01-26 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3b4f44a9f22"
down_revision: str | None = "666cc53a93be"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "user", "image_url", new_column_name="image", existing_type=sa.String()
    )


def downgrade() -> None:
    op.alter_column(
        "user", "image", new_column_name="image_url", existing_type=sa.String()
    )
