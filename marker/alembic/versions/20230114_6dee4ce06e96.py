"""Remove unused tables

Revision ID: 6dee4ce06e96
Revises: cc45a1a1c707
Create Date: 2023-01-14 19:31:40.470675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6dee4ce06e96'
down_revision = 'cc45a1a1c707'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_table("companies_comments")
    op.drop_table("projects_comments")
    op.drop_table("companies_persons")
    op.drop_table("projects_persons")

def downgrade():
    pass
