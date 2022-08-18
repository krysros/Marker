"""Rename investments to projects

Revision ID: 7fabe12d8b3f
Revises: b48c47f8e00a
Create Date: 2022-07-31 13:18:47.497203

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7fabe12d8b3f"
down_revision = "b48c47f8e00a"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(op.f("fk_investments_creator_id_users"), "investments")
    op.drop_constraint(op.f("fk_investments_editor_id_users"), "investments")
    op.drop_constraint(
        op.f("fk_companies_investments_investment_id_investments"),
        "companies_investments",
    )
    op.drop_constraint(
        op.f("fk_companies_investments_company_id_companies"), "companies_investments"
    )
    op.drop_constraint(op.f("fk_following_investment_id_investments"), "following")
    op.drop_constraint(op.f("fk_following_user_id_users"), "following")
    op.drop_constraint(op.f("pk_investments"), "investments")
    op.rename_table("investments", "projects")
    op.rename_table("companies_investments", "companies_projects")
    op.rename_table("following", "watched")
    op.alter_column(
        table_name="companies_projects",
        column_name="investment_id",
        new_column_name="project_id",
    )
    op.alter_column(
        table_name="watched", column_name="investment_id", new_column_name="project_id"
    )
    op.create_primary_key("pk_projects", "projects", ["id"])
    op.create_foreign_key(
        op.f("fk_projects_creator_id_users"),
        "projects",
        "users",
        ["creator_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_projects_editor_id_users"),
        "projects",
        "users",
        ["editor_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_companies_projects_project_id_projects"),
        "companies_projects",
        "projects",
        ["project_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_companies_projects_company_id_companies"),
        "companies_projects",
        "companies",
        ["company_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_watched_project_id_projects"),
        "watched",
        "projects",
        ["project_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_watched_user_id_users"),
        "watched",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(op.f("fk_projects_creator_id_users"), "projects")
    op.drop_constraint(op.f("fk_projects_editor_id_users"), "projects")
    op.drop_constraint(
        op.f("fk_companies_projects_project_id_projects"), "companies_projects"
    )
    op.drop_constraint(
        op.f("fk_companies_projects_company_id_projects"), "companies_projects"
    )
    op.drop_constraint(op.f("fk_watched_project_id_projects"), "watched")
    op.drop_constraint(op.f("fk_watched_user_id_users"), "watched")
    op.drop_constraint(op.f("pk_projects"), "projects")
    op.rename_table("projects", "investments")
    op.rename_table("companies_projects", "companies_investments")
    op.rename_table("watched", "following")
    op.alter_column(
        table_name="companies_investments",
        column_name="project_id",
        new_column_name="investment_id",
    )
    op.alter_column(
        table_name="following",
        column_name="project_id",
        new_column_name="investment_id",
    )
    op.create_primary_key("pk_investments", "investments", ["id"])
    op.create_foreign_key(
        op.f("fk_investments_creator_id_users"),
        "investments",
        "users",
        ["creator_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_investments_editor_id_users"),
        "investments",
        "users",
        ["editor_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_companies_investments_investment_id_investments"),
        "companies_investments",
        "investments",
        ["investment_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_companies_investments_company_id_companies"),
        "companies_investments",
        "companies",
        ["company_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_following_investment_id_investments"),
        "following",
        "investments",
        ["investment_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_following_user_id_users"),
        "following",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
