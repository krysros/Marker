"""Rename marker to checked

Revision ID: 84f8fbf101bd
Revises: 7fabe12d8b3f
Create Date: 2022-07-31 13:58:21.587105

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "84f8fbf101bd"
down_revision = "7fabe12d8b3f"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(op.f("fk_marker_company_id_companies"), "marker")
    op.drop_constraint(op.f("fk_marker_user_id_users"), "marker")
    op.rename_table("marker", "checked")
    op.create_foreign_key(
        op.f("fk_checked_company_id_companies"),
        "checked",
        "companies",
        ["company_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_checked_user_id_users"),
        "checked",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(op.f("fk_checked_company_id_companies"), "checked")
    op.drop_constraint(op.f("fk_checked_user_id_users"), "checked")
    op.rename_table("checked", "marker")
    op.create_foreign_key(
        op.f("fk_marker_company_id_companies"),
        "marker",
        "companies",
        ["company_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_marker_user_id_users"),
        "marker",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
