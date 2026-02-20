"""Demo surveys table + extend email_log type check.

Revision ID: 0008
Revises: 0007
Create Date: 2026-02-20
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS demo_surveys (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            teacher_id UUID NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
            useful TEXT,
            material TEXT,
            recommend TEXT,
            feedback TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    # Extend email_log type check to include 'upgrade' and 'invite'
    op.execute("ALTER TABLE email_log DROP CONSTRAINT IF EXISTS email_log_type_check")
    op.execute("ALTER TABLE email_log ADD CONSTRAINT email_log_type_check CHECK (type IN ('verify', 'reset', 'magic_link', 'upgrade', 'invite'))")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS demo_surveys CASCADE")
    op.execute("ALTER TABLE email_log DROP CONSTRAINT IF EXISTS email_log_type_check")
    op.execute("ALTER TABLE email_log ADD CONSTRAINT email_log_type_check CHECK (type IN ('verify', 'reset', 'magic_link'))")
