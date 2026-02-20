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
    op.execute("""
    DELETE FROM teachers
    WHERE password_hash IS NOT NULL AND password_hash NOT LIKE '$2b$%'
    """)

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
