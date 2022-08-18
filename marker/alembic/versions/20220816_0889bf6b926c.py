"""Rename category to color

Revision ID: 0889bf6b926c
Revises: 53b98313d0c6
Create Date: 2022-08-16 14:46:43.173157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0889bf6b926c'
down_revision = '53b98313d0c6'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column(table_name='companies', column_name='category', new_column_name='color')

def downgrade():
    op.alter_column(table_name='companies', column_name='color', new_column_name='category')
