"""Added themes table

Revision ID: 3cf8a15d4cf5
Revises: d113ef56aa61
Create Date: 2023-03-23 10:20:18.036958

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3cf8a15d4cf5"
down_revision = "d113ef56aa61"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "themes",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("theme", sa.Unicode(length=10), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_themes_user_id_users"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_themes")),
    )


def downgrade():
    op.drop_table("themes")
