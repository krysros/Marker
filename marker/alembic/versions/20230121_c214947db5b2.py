"""init

Revision ID: c214947db5b2
Revises: 
Create Date: 2023-01-21 19:20:12.268354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c214947db5b2"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Unicode(length=30), nullable=False),
        sa.Column("fullname", sa.Unicode(length=50), nullable=False),
        sa.Column("email", sa.Unicode(length=50), nullable=False),
        sa.Column("role", sa.Unicode(length=20), nullable=False),
        sa.Column("password", sa.Unicode(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("name", name=op.f("uq_users_name")),
    )
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Unicode(length=100), nullable=False),
        sa.Column("street", sa.Unicode(length=100), nullable=False),
        sa.Column("postcode", sa.Unicode(length=10), nullable=False),
        sa.Column("city", sa.Unicode(length=100), nullable=False),
        sa.Column("state", sa.Unicode(length=2), nullable=False),
        sa.Column("country", sa.Unicode(length=2), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("link", sa.Unicode(length=100), nullable=False),
        sa.Column("NIP", sa.Unicode(length=20), nullable=False),
        sa.Column("REGON", sa.Unicode(length=20), nullable=False),
        sa.Column("KRS", sa.Unicode(length=20), nullable=False),
        sa.Column("court", sa.Unicode(length=100), nullable=False),
        sa.Column("color", sa.Unicode(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("editor_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
            name=op.f("fk_companies_creator_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["editor_id"],
            ["users.id"],
            name=op.f("fk_companies_editor_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_companies")),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Unicode(length=200), nullable=False),
        sa.Column("street", sa.Unicode(length=100), nullable=False),
        sa.Column("postcode", sa.Unicode(length=10), nullable=False),
        sa.Column("city", sa.Unicode(length=100), nullable=False),
        sa.Column("state", sa.Unicode(length=2), nullable=False),
        sa.Column("country", sa.Unicode(length=2), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("link", sa.Unicode(length=2000), nullable=False),
        sa.Column("color", sa.Unicode(length=10), nullable=False),
        sa.Column("deadline", sa.Date(), nullable=False),
        sa.Column("stage", sa.Unicode(length=100), nullable=False),
        sa.Column("delivery_method", sa.Unicode(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("editor_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
            name=op.f("fk_projects_creator_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["editor_id"],
            ["users.id"],
            name=op.f("fk_projects_editor_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Unicode(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("editor_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
            name=op.f("fk_tags_creator_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["editor_id"],
            ["users.id"],
            name=op.f("fk_tags_editor_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tags")),
    )
    op.create_table(
        "checked",
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name=op.f("fk_checked_company_id_companies"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_checked_user_id_users"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("editor_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name=op.f("fk_comments_company_id_companies"),
        ),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
            name=op.f("fk_comments_creator_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["editor_id"],
            ["users.id"],
            name=op.f("fk_comments_editor_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_comments_project_id_projects"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comments")),
    )
    op.create_table(
        "companies_projects",
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("stage", sa.Unicode(length=100), nullable=False),
        sa.Column("role", sa.Unicode(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name=op.f("fk_companies_projects_company_id_companies"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_companies_projects_project_id_projects"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "company_id", "project_id", name=op.f("pk_companies_projects")
        ),
    )
    op.create_table(
        "companies_tags",
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("tag_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name=op.f("fk_companies_tags_company_id_companies"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
            name=op.f("fk_companies_tags_tag_id_tags"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    op.create_table(
        "persons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Unicode(length=100), nullable=False),
        sa.Column("position", sa.Unicode(length=100), nullable=False),
        sa.Column("phone", sa.Unicode(length=50), nullable=False),
        sa.Column("email", sa.Unicode(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("editor_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name=op.f("fk_persons_company_id_companies"),
        ),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
            name=op.f("fk_persons_creator_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["editor_id"],
            ["users.id"],
            name=op.f("fk_persons_editor_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], name=op.f("fk_persons_project_id_projects")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_persons")),
    )
    op.create_table(
        "projects_tags",
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("tag_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_projects_tags_project_id_projects"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tags.id"],
            name=op.f("fk_projects_tags_tag_id_tags"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    op.create_table(
        "recommended",
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name=op.f("fk_recommended_company_id_companies"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_recommended_user_id_users"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    op.create_table(
        "watched",
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_watched_project_id_projects"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_watched_user_id_users"),
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("watched")
    op.drop_table("recommended")
    op.drop_table("projects_tags")
    op.drop_table("persons")
    op.drop_table("companies_tags")
    op.drop_table("companies_projects")
    op.drop_table("comments")
    op.drop_table("checked")
    op.drop_table("tags")
    op.drop_table("projects")
    op.drop_table("companies")
    op.drop_table("users")
    # ### end Alembic commands ###