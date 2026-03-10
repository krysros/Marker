"""Cleanup stale selected_* and *_stars rows

Revision ID: 6f7a9c1e2b3d
Revises: d3a6f1b2c9e4
Create Date: 2026-03-09 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6f7a9c1e2b3d"
down_revision = "d3a6f1b2c9e4"
branch_labels = None
depends_on = None


def _cleanup_user_item_table(table_name, item_column, item_table):
    op.execute(sa.text(f"""
            DELETE FROM {table_name}
            WHERE user_id IS NULL
               OR {item_column} IS NULL
               OR user_id NOT IN (SELECT id FROM users)
               OR {item_column} NOT IN (SELECT id FROM {item_table})
            """))


def upgrade():
    _cleanup_user_item_table("companies_stars", "company_id", "companies")
    _cleanup_user_item_table("projects_stars", "project_id", "projects")
    _cleanup_user_item_table("selected_companies", "company_id", "companies")
    _cleanup_user_item_table("selected_projects", "project_id", "projects")
    _cleanup_user_item_table("selected_tags", "tag_id", "tags")
    _cleanup_user_item_table("selected_contacts", "contact_id", "contacts")


def downgrade():
    # Data cleanup migration has no deterministic downgrade.
    pass
