"""Didacta mode: demo_mode toggle + demo_expires_at for temp accounts.

Revision ID: 0006
Revises: 0005
Create Date: 2026-02-19
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # demo_mode: admin-only toggle to enable "Demo starten" on login page
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS demo_mode BOOLEAN DEFAULT FALSE")
    # demo_expires_at: when a demo account expires (7 days after creation)
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS demo_expires_at TIMESTAMPTZ")


def downgrade() -> None:
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS demo_mode")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS demo_expires_at")
