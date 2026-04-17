"""Add object_category to Project

Revision ID: 9ca296fb5e5a
Revises: a1b2c3d4e5f6
Create Date: 2026-04-16 21:39:23.230758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ca296fb5e5a'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('projects', sa.Column('object_category', sa.String(), nullable=True))

def downgrade():
    op.drop_column('projects', 'object_category')
