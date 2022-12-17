"""Short column name

Revision ID: e6f6e7b09b7c
Revises: 3743c4aa626e
Create Date: 2022-12-17 11:52:35.902652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e6f6e7b09b7c"
down_revision = "3743c4aa626e"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        table_name="projects",
        column_name="project_delivery_method",
        new_column_name="delivery_method",
    )


def downgrade():
    op.alter_column(
        table_name="projects",
        column_name="delivery_method",
        new_column_name="project_delivery_method",
    )
