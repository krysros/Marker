"""add indexes on stars tables

Revision ID: add_stars_indexes
Revises: 9ca296fb5e5a
Create Date: 2026-05-19

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_stars_indexes"
down_revision = "9ca296fb5e5a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_companies_stars_company_id", "companies_stars", ["company_id"])
    op.create_index("ix_companies_stars_user_id", "companies_stars", ["user_id"])
    op.create_index("ix_projects_stars_project_id", "projects_stars", ["project_id"])
    op.create_index("ix_projects_stars_user_id", "projects_stars", ["user_id"])


def downgrade():
    op.drop_index("ix_companies_stars_company_id", table_name="companies_stars")
    op.drop_index("ix_companies_stars_user_id", table_name="companies_stars")
    op.drop_index("ix_projects_stars_project_id", table_name="projects_stars")
    op.drop_index("ix_projects_stars_user_id", table_name="projects_stars")
