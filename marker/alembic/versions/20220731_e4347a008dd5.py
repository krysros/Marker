"""Rename fullname to name

Revision ID: e4347a008dd5
Revises: 870e6a30fd27
Create Date: 2022-07-31 16:34:51.831853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4347a008dd5"
down_revision = "870e6a30fd27"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        table_name="persons", column_name="fullname", new_column_name="name"
    )


def downgrade():
    op.alter_column(
        table_name="persons", column_name="name", new_column_name="fullname"
    )
