"""Rename unique user constraint

Revision ID: a671309fcb03
Revises: c2dfed717d4e
Create Date: 2022-07-31 15:13:37.197634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a671309fcb03"
down_revision = "c2dfed717d4e"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.create_unique_constraint(op.f("uq_users_name"), "users", ["name"])


def downgrade():
    op.drop_constraint("uq_users_name", "users", type_="unique")
    op.create_unique_constraint(op.f("uq_users_username"), "users", ["username"])
