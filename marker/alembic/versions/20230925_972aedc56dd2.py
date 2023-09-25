"""Rename columns

Revision ID: 972aedc56dd2
Revises: c07454788650
Create Date: 2023-09-25 08:48:17.136746

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "972aedc56dd2"
down_revision = "c07454788650"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("identification_numbers", "sad", new_column_name="court")


def downgrade():
    op.alter_column("identification_numbers", "court", new_column_name="sad")
