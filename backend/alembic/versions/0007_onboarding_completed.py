"""Add onboarding_completed column to user_profiles.

Revision ID: 0007
Revises: 0006
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_profiles",
        sa.Column("onboarding_completed", sa.Boolean(), server_default="false", nullable=False),
    )
    # Backfill: mark existing users with profile data as onboarded
    op.execute(
        "UPDATE user_profiles SET onboarding_completed = true "
        "WHERE bundesland IS NOT NULL OR schulform IS NOT NULL OR faecher IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_column("user_profiles", "onboarding_completed")
