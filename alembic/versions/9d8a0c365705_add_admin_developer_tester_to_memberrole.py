"""add admin developer tester to memberrole

Revision ID: 9d8a0c365705
Revises: 01df453c5299
Create Date: 2026-10-02 12:57:06.391728

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9d8a0c365705'
down_revision: str | Sequence[str] | None = '01df453c5299'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE memberrole ADD VALUE IF NOT EXISTS 'admin'")
    op.execute("ALTER TYPE memberrole ADD VALUE IF NOT EXISTS 'developer'")
    op.execute("ALTER TYPE memberrole ADD VALUE IF NOT EXISTS 'tester'")


def downgrade() -> None:
    """Downgrade schema."""
