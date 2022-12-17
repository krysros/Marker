"""Add projects_persons table

Revision ID: 7be5a4df6711
Revises: d19f09e154a7
Create Date: 2022-12-17 12:28:58.091748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7be5a4df6711"
down_revision = "d19f09e154a7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects_persons",
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("person_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_projects_persons_project_id_projects"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["person_id"],
            ["persons.id"],
            name=op.f("fk_projects_persons_person_id_persons"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )


def downgrade():
    op.drop_table("projects_persons")
