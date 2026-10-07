"""add scheme translations column

Revision ID: ec8e8a5176b6
Revises: 57cbad419aba
Create Date: 2026-09-28 21:23:08.559249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec8e8a5176b6'
down_revision: Union[str, None] = '57cbad419aba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Autogenerate produced `nullable=False` with no default, which fails
    # against any pre-existing rows (NotNullViolation) — a fresh table has
    # none, but this exact migration crash-looped the app against the
    # docker-compose demo's already-seeded database. A server_default lets
    # existing rows backfill to '{}' (no translations yet, falls back to
    # English) while new rows still require the column going forward.
    op.add_column('schemes', sa.Column('translations', sa.JSON(), nullable=False, server_default='{}'))
    op.alter_column('schemes', 'translations', server_default=None)


def downgrade() -> None:
    op.drop_column('schemes', 'translations')
