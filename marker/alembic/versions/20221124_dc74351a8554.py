"""Rename WWW to link in companies

Revision ID: dc74351a8554
Revises: c87ad4fb1cf7
Create Date: 2022-11-24 22:07:20.963972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dc74351a8554"
down_revision = "c87ad4fb1cf7"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(table_name="companies", column_name="WWW", new_column_name="link")


def downgrade():
    op.alter_column(table_name="companies", column_name="link", new_column_name="WWW")
