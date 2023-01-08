"""Fix id default constraints

Revision ID: 5ed8962317d9
Revises: 62d988387185
Create Date: 2023-01-08 11:57:34.244964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5ed8962317d9"
down_revision = "62d988387185"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER SEQUENCE branches_id_seq RENAME TO tags_id_seq")
    op.execute("ALTER SEQUENCE tenders_id_seq RENAME TO projects_id_seq")
    op.alter_column(
        "companies",
        "id",
        server_default=sa.text("nextval('companies_id_seq'::regclass)"),
    )
    op.alter_column(
        "tags", "id", server_default=sa.text("nextval('tags_id_seq'::regclass)")
    )
    op.alter_column(
        "projects", "id", server_default=sa.text("nextval('projects_id_seq'::regclass)")
    )


def downgrade():
    op.execute("ALTER SEQUENCE tags_id_seq RENAME TO branches_id_seq")
    op.execute("ALTER SEQUENCE projects_id_seq RENAME TO tenders_id_seq")
    op.alter_column("companies", "id", server_default=None)
    op.alter_column(
        "tags", "id", server_default=sa.text("nextval('branches_id_seq'::regclass)")
    )
    op.alter_column(
        "projects", "id", server_default=sa.text("nextval('tenders_id_seq'::regclass)")
    )
