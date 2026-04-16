"""Move currency, value_net, value_gross from projects to activity

Revision ID: a1b2c3d4e5f6
Revises: 6ae8eb2273ab
Create Date: 2026-04-16 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "6ae8eb2273ab"
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to activity table
    op.add_column("activity", sa.Column("currency", sa.String(), nullable=True))
    op.add_column("activity", sa.Column("value_net", sa.Numeric(), nullable=True))
    op.add_column("activity", sa.Column("value_gross", sa.Numeric(), nullable=True))

    # Copy data from projects to activity (each project's values go to all its activities)
    op.execute("""
        UPDATE activity
        SET currency = projects.currency,
            value_net = projects.value_net,
            value_gross = projects.value_gross
        FROM projects
        WHERE activity.project_id = projects.id
        """)

    # Drop columns from projects table
    op.drop_column("projects", "currency")
    op.drop_column("projects", "value_net")
    op.drop_column("projects", "value_gross")


def downgrade():
    # Add columns back to projects table
    op.add_column("projects", sa.Column("currency", sa.String(), nullable=True))
    op.add_column("projects", sa.Column("value_net", sa.Numeric(), nullable=True))
    op.add_column("projects", sa.Column("value_gross", sa.Numeric(), nullable=True))

    # Copy data back: take the first non-null value from activity for each project
    op.execute("""
        UPDATE projects
        SET currency = sub.currency,
            value_net = sub.value_net,
            value_gross = sub.value_gross
        FROM (
            SELECT DISTINCT ON (project_id)
                project_id, currency, value_net, value_gross
            FROM activity
            WHERE currency IS NOT NULL
               OR value_net IS NOT NULL
               OR value_gross IS NOT NULL
            ORDER BY project_id, company_id
        ) sub
        WHERE projects.id = sub.project_id
        """)

    # Drop columns from activity table
    op.drop_column("activity", "currency")
    op.drop_column("activity", "value_net")
    op.drop_column("activity", "value_gross")
