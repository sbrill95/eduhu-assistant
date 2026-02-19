"""Set admin roles for existing admin accounts.

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
    # Set known admin accounts (by name or password)
    # Steffen (krake26), Christopher (leopard26) get admin role
    op.execute("""
    UPDATE teachers
    SET role = 'admin'
    WHERE password IN ('krake26', 'leopard26')
    """)


def downgrade() -> None:
    op.execute("""
    UPDATE teachers
    SET role = 'teacher'
    WHERE password IN ('krake26', 'leopard26')
    """)
