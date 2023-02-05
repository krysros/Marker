"""Rename person to contact

Revision ID: 6009f105eac8
Revises: 1c7f35b54901
Create Date: 2023-02-05 08:28:24.654103

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6009f105eac8'
down_revision = '1c7f35b54901'
branch_labels = None
depends_on = None

def upgrade():
    op.rename_table(old_table_name="persons", new_table_name="contacts")

def downgrade():
    op.rename_table(old_table_name="contacts", new_table_name="persons")
