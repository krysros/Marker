"""Rename columns

Revision ID: 39a2989cf4d7
Revises: 972aedc56dd2
Create Date: 2023-09-25 09:20:35.399772

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39a2989cf4d7'
down_revision = '972aedc56dd2'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('companies', 'link', new_column_name='website')
    op.alter_column('projects', 'link', new_column_name='website')


def downgrade():
    op.alter_column('companies', 'website', new_column_name='link')
    op.alter_column('projects', 'website', new_column_name='link')
