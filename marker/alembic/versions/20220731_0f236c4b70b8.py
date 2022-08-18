"""Rename upvotes to thumbs_up

Revision ID: 0f236c4b70b8
Revises: 84f8fbf101bd
Create Date: 2022-07-31 14:11:34.450959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0f236c4b70b8"
down_revision = "84f8fbf101bd"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(op.f("fk_upvotes_company_id_companies"), "upvotes")
    op.drop_constraint(op.f("fk_upvotes_user_id_users"), "upvotes")
    op.rename_table("upvotes", "thumbs_up")
    op.create_foreign_key(
        op.f("fk_thumbs_up_company_id_companies"),
        "thumbs_up",
        "companies",
        ["company_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_thumbs_up_user_id_users"),
        "thumbs_up",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(op.f("fk_thumbs_up_company_id_companies"), "thumbs_up")
    op.drop_constraint(op.f("fk_thumbs_up_user_id_users"), "thumbs_up")
    op.rename_table("thumbs_up", "upvotes")
    op.create_foreign_key(
        op.f("fk_upvotes_company_id_companies"),
        "upvotes",
        "companies",
        ["company_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_upvotes_user_id_users"),
        "upvotes",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
