"""Add color to project

Revision ID: 3743c4aa626e
Revises: dc74351a8554
Create Date: 2022-11-24 22:24:35.568001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3743c4aa626e'
down_revision = 'dc74351a8554'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("projects", sa.Column("color", sa.Unicode(10), server_default=""))

def downgrade():
    op.drop_column("projects", "color")
