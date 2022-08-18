"""Drop documents table

Revision ID: 578bdc35e716
Revises: 0f236c4b70b8
Create Date: 2022-07-31 14:13:25.318874

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "578bdc35e716"
down_revision = "0f236c4b70b8"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("documents")


def downgrade():
    op.create_table(
        "documents",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "filename", sa.VARCHAR(length=200), autoincrement=False, nullable=True
        ),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column("creator_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("editor_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("typ", sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
            name="fk_documents_creator_id_users",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["editor_id"],
            ["users.id"],
            name="fk_documents_editor_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
    )
