"""Additional columns in companies_projects table

Revision ID: 257985e0bffb
Revises: 5ed8962317d9
Create Date: 2023-01-08 21:01:06.224166

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "257985e0bffb"
down_revision = "5ed8962317d9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "companies_projects", sa.Column("stage", sa.Unicode(length=100), nullable=True)
    )
    op.add_column(
        "companies_projects", sa.Column("role", sa.Unicode(length=100), nullable=True)
    )


def downgrade():
    op.drop_column("companies_projects", "stage")
    op.drop_column("companies_projects", "role")
