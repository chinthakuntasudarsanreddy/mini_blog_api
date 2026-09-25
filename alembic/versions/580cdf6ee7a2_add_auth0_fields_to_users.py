"""add auth0 fields to users

Revision ID: 580cdf6ee7a2
Revises: 5bde85b0f4fc
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "580cdf6ee7a2"
down_revision: Union[str, Sequence[str], None] = "5bde85b0f4fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Auth0 fields to users table."""

    # provider was already added during the previous partial migration.
    # Therefore, only add it if it does not already exist.
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    if "provider" not in existing_columns:
        op.add_column(
            "users",
            sa.Column(
                "provider",
                sa.String(length=50),
                nullable=False,
                server_default="local",
            ),
        )

    if "provider_id" not in existing_columns:
        op.add_column(
            "users",
            sa.Column(
                "provider_id",
                sa.String(length=255),
                nullable=True,
            ),
        )

    # Check indexes because the migration may have partially completed.
    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("users")
    }

    if "ix_users_provider_id" not in existing_indexes:
        op.create_index(
            "ix_users_provider_id",
            "users",
            ["provider_id"],
            unique=True,
        )


def downgrade() -> None:
    """Remove Auth0 fields from users table."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("users")
    }

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    if "ix_users_provider_id" in existing_indexes:
        op.drop_index(
            "ix_users_provider_id",
            table_name="users",
        )

    if "provider_id" in existing_columns:
        op.drop_column(
            "users",
            "provider_id",
        )

    if "provider" in existing_columns:
        op.drop_column(
            "users",
            "provider",
        )