"""Add indexes for tag association filters

Revision ID: 4fd5be91a2c7
Revises: 9c1d6e7a4b2f
Create Date: 2026-03-08 11:30:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "4fd5be91a2c7"
down_revision = "9c1d6e7a4b2f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        op.f("ix_companies_tags_tag_id"),
        "companies_tags",
        ["tag_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_projects_tags_project_id"),
        "projects_tags",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_projects_tags_tag_id"),
        "projects_tags",
        ["tag_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_projects_tags_tag_id"), table_name="projects_tags")
    op.drop_index(op.f("ix_projects_tags_project_id"), table_name="projects_tags")
    op.drop_index(op.f("ix_companies_tags_tag_id"), table_name="companies_tags")
