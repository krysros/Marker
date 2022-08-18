"""Update projects table

Revision ID: c2dfed717d4e
Revises: 138c1964c16a
Create Date: 2022-07-31 15:04:17.456116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c2dfed717d4e"
down_revision = "138c1964c16a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects", sa.Column("street", sa.Unicode(length=100), nullable=True)
    )
    op.add_column(
        "projects", sa.Column("postcode", sa.Unicode(length=10), nullable=True)
    )
    op.add_column("projects", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("projects", sa.Column("longitude", sa.Float(), nullable=True))
    op.add_column("projects", sa.Column("stage", sa.Unicode(length=100), nullable=True))
    op.add_column(
        "projects",
        sa.Column("project_delivery_method", sa.Unicode(length=100), nullable=True),
    )
    op.alter_column(
        table_name="projects", column_name="voivodeship", new_column_name="state"
    )


def downgrade():
    op.drop_column("projects", "street")
    op.drop_column("projects", "postcode")
    op.drop_column("projects", "latitude")
    op.drop_column("projects", "longitude")
    op.drop_column("projects", "stage")
    op.drop_column("projects", "project_delivery_method")
    op.alter_column(
        table_name="projects", column_name="state", new_column_name="voivodeship"
    )
