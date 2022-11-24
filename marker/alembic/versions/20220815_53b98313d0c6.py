"""Rename thumbs_up to recomended

Revision ID: 53b98313d0c6
Revises: 39a9144f106b
Create Date: 2022-08-15 20:21:26.975087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "53b98313d0c6"
down_revision = "39a9144f106b"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(op.f("fk_thumbs_up_company_id_companies"), "thumbs_up")
    op.drop_constraint(op.f("fk_thumbs_up_user_id_users"), "thumbs_up")
    op.rename_table("thumbs_up", "recomended")
    op.create_foreign_key(
        op.f("fk_recomended_company_id_companies"),
        "recomended",
        "companies",
        ["company_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_recomended_user_id_users"),
        "recomended",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(op.f("fk_recomended_company_id_companies"), "recomended")
    op.drop_constraint(op.f("fk_recomended_user_id_users"), "recomended")
    op.rename_table("recomended", "thumbs_up")
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
