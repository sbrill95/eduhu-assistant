"""Clean up legacy plaintext accounts and set admin roles by email.

Revision ID: 0006
Revises: 0005
Create Date: 2026-02-19

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Delete legacy accounts whose password_hash contains plaintext
    # (migration 0005 copied plaintext passwords without hashing)
    # bcrypt hashes always start with '$2b$'
    # Must delete dependent rows first (no ON DELETE CASCADE on these FKs)
    legacy_filter = "SELECT id FROM teachers WHERE password_hash IS NOT NULL AND password_hash NOT LIKE '$2b$%'"
    # 0001: core tables
    op.execute(f"DELETE FROM session_logs WHERE user_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM user_memories WHERE user_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM teacher_entities WHERE user_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM conversations WHERE user_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM user_curricula WHERE user_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM user_profiles WHERE id IN ({legacy_filter})")
    # 0002: materials
    op.execute(f"DELETE FROM generated_materials WHERE teacher_id IN ({legacy_filter})")
    # 0003: coolify tables
    op.execute(f"DELETE FROM exercises WHERE teacher_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM exercise_pages WHERE teacher_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM todos WHERE teacher_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM polls WHERE teacher_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM agent_sessions WHERE teacher_id IN ({legacy_filter})")
    op.execute(f"DELETE FROM audio_pages WHERE teacher_id IN ({legacy_filter})")
    # 0004: token usage
    op.execute(f"DELETE FROM token_usage WHERE teacher_id IN ({legacy_filter})")
    # Finally: teachers
    op.execute(f"DELETE FROM teachers WHERE id IN ({legacy_filter})")

    # Set admin role by email
    op.execute("""
    UPDATE teachers
    SET role = 'admin'
    WHERE email IN ('c.utsch@eduhu.de', 's.brill@eduhu.de')
    """)


def downgrade() -> None:
    op.execute("""
    UPDATE teachers
    SET role = 'teacher'
    WHERE email IN ('c.utsch@eduhu.de', 's.brill@eduhu.de')
    """)
