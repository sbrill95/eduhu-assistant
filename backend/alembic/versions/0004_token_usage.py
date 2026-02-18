"""Token usage tracking table.

Revision ID: 0004
Revises: 0003
Create Date: 2026-02-18
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS token_usage (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      teacher_id UUID NOT NULL REFERENCES teachers(id),
      model TEXT NOT NULL,
      input_tokens INT NOT NULL DEFAULT 0,
      output_tokens INT NOT NULL DEFAULT 0,
      cost_usd NUMERIC(12, 6) NOT NULL DEFAULT 0,
      agent_type TEXT DEFAULT 'main',
      request_id TEXT,
      created_at TIMESTAMPTZ DEFAULT now()
    )
    """)
    op.execute("""
    CREATE INDEX IF NOT EXISTS idx_token_usage_teacher_created
      ON token_usage(teacher_id, created_at DESC)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS token_usage CASCADE")
