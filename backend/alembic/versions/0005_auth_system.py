"""Auth system: email login, JWT, roles, email logging.

Revision ID: 0005
Revises: 0004
Create Date: 2026-02-18
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add auth columns to teachers
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS email TEXT UNIQUE")
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS password_hash TEXT")
    op.execute("""
        ALTER TABLE teachers ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'teacher'
        CHECK (role IN ('admin', 'teacher', 'demo'))
    """)
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE")
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS magic_link_token TEXT")
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS magic_link_expires TIMESTAMPTZ")
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS reset_token TEXT")
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMPTZ")

    # Migrate old password data to password_hash, then drop old column
    op.execute("UPDATE teachers SET password_hash = password WHERE password_hash IS NULL AND password IS NOT NULL")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS password")

    # Indexes for token lookups
    op.execute("CREATE INDEX IF NOT EXISTS idx_teachers_email ON teachers(email)")
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_teachers_magic_link
        ON teachers(magic_link_token) WHERE magic_link_token IS NOT NULL
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_teachers_reset_token
        ON teachers(reset_token) WHERE reset_token IS NOT NULL
    """)

    # Email log table
    op.execute("""
        CREATE TABLE IF NOT EXISTS email_log (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            recipient TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('verify', 'reset', 'magic_link')),
            status TEXT DEFAULT 'queued' CHECK (status IN ('queued', 'sent', 'failed')),
            error_message TEXT,
            attempts INTEGER DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            sent_at TIMESTAMPTZ
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_email_log_recipient ON email_log(recipient)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_email_log_status ON email_log(status) WHERE status = 'queued'")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS email_log CASCADE")
    op.execute("DROP INDEX IF EXISTS idx_teachers_reset_token")
    op.execute("DROP INDEX IF EXISTS idx_teachers_magic_link")
    op.execute("DROP INDEX IF EXISTS idx_teachers_email")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS reset_token_expires")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS reset_token")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS magic_link_expires")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS magic_link_token")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS email_verified")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS role")
    # Restore old password column BEFORE dropping password_hash
    op.execute("ALTER TABLE teachers ADD COLUMN IF NOT EXISTS password TEXT NOT NULL DEFAULT ''")
    op.execute("UPDATE teachers SET password = password_hash WHERE password_hash IS NOT NULL")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS password_hash")
    op.execute("ALTER TABLE teachers DROP COLUMN IF EXISTS email")
