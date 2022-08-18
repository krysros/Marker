"""Update companies table

Revision ID: 138c1964c16a
Revises: 020e54cf08a7
Create Date: 2022-07-31 14:39:03.852915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "138c1964c16a"
down_revision = "020e54cf08a7"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(table_name="companies", column_name="nip", new_column_name="NIP")
    op.alter_column(
        table_name="companies", column_name="regon", new_column_name="REGON"
    )
    op.alter_column(table_name="companies", column_name="krs", new_column_name="KRS")
    op.alter_column(table_name="companies", column_name="www", new_column_name="WWW")
    op.alter_column(
        table_name="companies", column_name="voivodeship", new_column_name="state"
    )
    op.add_column("companies", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("companies", sa.Column("longitude", sa.Float(), nullable=True))


def downgrade():
    op.alter_column(table_name="companies", column_name="NIP", new_column_name="nip")
    op.alter_column(
        table_name="companies", column_name="REGON", new_column_name="regon"
    )
    op.alter_column(table_name="companies", column_name="KRS", new_column_name="krs")
    op.alter_column(
        table_name="companies", column_name="state", new_column_name="voivodeship"
    )
    op.drop_column("companies", "latitude")
    op.drop_column("companies", "longitude")
