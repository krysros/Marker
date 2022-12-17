"""Add projects_comments table

Revision ID: 62d988387185
Revises: 7be5a4df6711
Create Date: 2022-12-17 14:46:59.147697

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62d988387185'
down_revision = '7be5a4df6711'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "projects_comments",
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("comment_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["comment_id"],
            ["comments.id"],
            name=op.f("fk_projects_comments_comment_id_comments"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_projects_comments_project_id_projects"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )

def downgrade():
    op.drop_table("projects_comments")
