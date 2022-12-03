"""Rename recommended to recommended

Revision ID: c87ad4fb1cf7
Revises: 2bb39756db52
Create Date: 2022-11-24 19:26:49.419101

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c87ad4fb1cf7"
down_revision = "2bb39756db52"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(op.f("fk_recomended_company_id_companies"), "recomended")
    op.drop_constraint(op.f("fk_recomended_user_id_users"), "recomended")
    op.rename_table("recomended", "recommended")
    op.create_foreign_key(
        op.f("fk_recommended_company_id_companies"),
        "recommended",
        "companies",
        ["company_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_recommended_user_id_users"),
        "recommended",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(op.f("fk_recommended_company_id_companies"), "recommended")
    op.drop_constraint(op.f("fk_recommended_user_id_users"), "recommended")
    op.rename_table("recommended", "recomended")
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
