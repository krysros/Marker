"""Change person constraints

Revision ID: f704f50bad1a
Revises: 6009f105eac8
Create Date: 2023-02-05 08:54:36.759204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f704f50bad1a'
down_revision = '6009f105eac8'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_constraint(op.f("pk_persons"), "contacts")
    op.drop_constraint(op.f("fk_persons_company_id_companies"), "contacts")
    op.drop_constraint(op.f("fk_persons_project_id_projects"), "contacts")
    op.drop_constraint(op.f("fk_persons_creator_id_users"), "contacts")
    op.drop_constraint(op.f("fk_persons_editor_id_users"), "contacts")
    op.create_primary_key("pk_contacts", "contacts", ["id"])
    op.create_foreign_key(
        op.f("fk_contacts_company_id_companies"),
        "contacts",
        "companies",
        ["company_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_contacts_project_id_projects"),
        "contacts",
        "projects",
        ["project_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_contacts_creator_id_users"),
        "contacts",
        "users",
        ["creator_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_contacts_editor_id_users"),
        "contacts",
        "users",
        ["editor_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint(op.f("pk_contacts"), "contacts")
    op.drop_constraint(op.f("fk_contacts_company_id_companies"), "contacts")
    op.drop_constraint(op.f("fk_contacts_project_id_projects"), "contacts")
    op.drop_constraint(op.f("fk_contacts_creator_id_users"), "contacts")
    op.drop_constraint(op.f("fk_contacts_editor_id_users"), "contacts")
    op.create_primary_key("pk_persons", "contacts", ["id"])
    op.create_foreign_key(
        op.f("fk_persons_company_id_companies"),
        "contacts",
        "companies",
        ["company_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_persons_project_id_projects"),
        "contacts",
        "projects",
        ["project_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("fk_persons_creator_id_users"),
        "contacts",
        "users",
        ["creator_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        op.f("fk_persons_editor_id_users"),
        "contacts",
        "users",
        ["editor_id"],
        ["id"],
        ondelete="SET NULL",
    )
