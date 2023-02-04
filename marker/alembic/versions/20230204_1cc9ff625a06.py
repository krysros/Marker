"""Rename position to role

Revision ID: 1c7f35b54901
Revises: c214947db5b2
Create Date: 2023-02-04 22:23:30.546211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cc9ff625a06'
down_revision = 'c214947db5b2'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column(
        table_name="companies", column_name="state", new_column_name="region"
    )
    op.alter_column(
        table_name="projects", column_name="state", new_column_name="region"
    )

def downgrade():
    op.alter_column(
        table_name="companies", column_name="region", new_column_name="state"
    )
    op.alter_column(
        table_name="projects", column_name="region", new_column_name="state"
    )
