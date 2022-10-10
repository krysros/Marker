"""Add country column

Revision ID: 2bb39756db52
Revises: 0889bf6b926c
Create Date: 2022-10-10 13:20:27.118263

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bb39756db52'
down_revision = '0889bf6b926c'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('companies', sa.Column('country', sa.Unicode(2), server_default=""))
    op.add_column('projects', sa.Column('country', sa.Unicode(2), server_default=""))

def downgrade():
    op.drop_column('companies', 'country')
    op.drop_column('projects', 'country')
