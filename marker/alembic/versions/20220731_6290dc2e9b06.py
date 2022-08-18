"""Rename username to name

Revision ID: 6290dc2e9b06
Revises: 578bdc35e716
Create Date: 2022-07-31 14:14:24.638772

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6290dc2e9b06'
down_revision = '578bdc35e716'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column(table_name='users', column_name='username', new_column_name='name')

def downgrade():
    op.alter_column(table_name='users', column_name='name', new_column_name='username')
