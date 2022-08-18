"""Remove unused columns from companies

Revision ID: 870e6a30fd27
Revises: a671309fcb03
Create Date: 2022-07-31 16:28:19.558859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "870e6a30fd27"
down_revision = "a671309fcb03"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("companies", "phone")
    op.drop_column("companies", "email")


def downgrade():
    op.add_column(
        "companies",
        sa.Column("phone", sa.VARCHAR(length=150), autoincrement=False, nullable=True),
    )
    op.add_column(
        "companies",
        sa.Column("email", sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    )
