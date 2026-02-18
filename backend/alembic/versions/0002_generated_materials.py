"""Generated materials table.

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-12
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS generated_materials (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        teacher_id UUID REFERENCES teachers(id),
        type TEXT NOT NULL,
        content_json JSONB NOT NULL,
        docx_base64 TEXT,
        created_at TIMESTAMPTZ DEFAULT now()
    )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS generated_materials CASCADE")
