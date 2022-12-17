"""Add projects_tags table

Revision ID: d19f09e154a7
Revises: e6f6e7b09b7c
Create Date: 2022-12-17 12:21:37.035268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d19f09e154a7"
down_revision = "e6f6e7b09b7c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects_tags",
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("tag_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
            name=op.f("fk_projects_tags_tag_id_tags"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_projects_tags_project_id_projects"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )


def downgrade():
    op.drop_table("projects_tags")
