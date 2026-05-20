"""add chapter tracking columns to series

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-19
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("series", sa.Column("last_chapter_id", sa.String(), nullable=True))
    op.add_column("series", sa.Column("last_chapter_title", sa.String(), nullable=True))
    op.add_column("series", sa.Column("last_chapter_url", sa.String(), nullable=True))
    op.add_column("series", sa.Column("last_polled_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("series", "last_polled_at")
    op.drop_column("series", "last_chapter_url")
    op.drop_column("series", "last_chapter_title")
    op.drop_column("series", "last_chapter_id")
