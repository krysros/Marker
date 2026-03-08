"""Add selected table composite indexes

Revision ID: d3a6f1b2c9e4
Revises: 4fd5be91a2c7
Create Date: 2026-03-08 13:10:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "d3a6f1b2c9e4"
down_revision = "4fd5be91a2c7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_selected_companies_user_company",
        "selected_companies",
        ["user_id", "company_id"],
        unique=False,
    )
    op.create_index(
        "ix_selected_projects_user_project",
        "selected_projects",
        ["user_id", "project_id"],
        unique=False,
    )
    op.create_index(
        "ix_selected_tags_user_tag",
        "selected_tags",
        ["user_id", "tag_id"],
        unique=False,
    )
    op.create_index(
        "ix_selected_contacts_user_contact",
        "selected_contacts",
        ["user_id", "contact_id"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_selected_contacts_user_contact", table_name="selected_contacts")
    op.drop_index("ix_selected_tags_user_tag", table_name="selected_tags")
    op.drop_index("ix_selected_projects_user_project", table_name="selected_projects")
    op.drop_index("ix_selected_companies_user_company", table_name="selected_companies")
