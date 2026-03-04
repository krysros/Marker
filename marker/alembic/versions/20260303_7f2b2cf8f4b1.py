"""Add user deletion rate-limit fields

Revision ID: 7f2b2cf8f4b1
Revises: 163919059dcc
Create Date: 2026-03-03 22:10:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7f2b2cf8f4b1"
down_revision = "163919059dcc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users", sa.Column("delete_window_start", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column(
            "delete_window_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "users", sa.Column("delete_blocked_until", sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column("users", "delete_blocked_until")
    op.drop_column("users", "delete_window_count")
    op.drop_column("users", "delete_window_start")
