"""Rename recommended and watched to stars and companies_projects to activity

Revision ID: 1482d0eaac56
Revises: d09762e9f539
Create Date: 2023-06-11 12:09:26.629918

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1482d0eaac56"
down_revision = "d09762e9f539"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("recommended", "companies_stars")
    op.rename_table("watched", "projects_stars")
    op.rename_table("companies_projects", "activity")


def downgrade():
    op.rename_table("companies_stars", "recommended")
    op.rename_table("projects_stars", "watched")
    op.rename_table("activity", "companies_projects")
