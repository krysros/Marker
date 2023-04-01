"""Rename region to subdivision

Revision ID: d09762e9f539
Revises: 3cf8a15d4cf5
Create Date: 2023-04-01 21:53:48.952564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd09762e9f539'
down_revision = '3cf8a15d4cf5'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column("companies", column_name="region", new_column_name="subdivision")
    op.alter_column("projects", column_name="region", new_column_name="subdivision")

def downgrade():
    op.alter_column("companies", column_name="subdivision", new_column_name="region")
    op.alter_column("projects", column_name="subdivision", new_column_name="region")
