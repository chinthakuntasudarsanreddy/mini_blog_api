"""allow null password for auth0 users

Revision ID: 165ebe663f06
Revises: 580cdf6ee7a2
Create Date: 2026-09-25 18:07:43.812356

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "165ebe663f06"
down_revision: Union[str, Sequence[str], None] = "580cdf6ee7a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "password",
            existing_type=sa.String(length=255),
            existing_nullable=False,
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "password",
            existing_type=sa.String(length=255),
            existing_nullable=True,
            nullable=False,
        )