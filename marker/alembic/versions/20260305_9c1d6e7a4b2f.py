"""Set ON DELETE CASCADE on contacts.project_id

Revision ID: 9c1d6e7a4b2f
Revises: 2a6f4a9d1c3e
Create Date: 2026-03-05 12:55:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9c1d6e7a4b2f"
down_revision = "2a6f4a9d1c3e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("contacts", schema=None) as batch_op:
        batch_op.drop_constraint(
            op.f("fk_contacts_project_id_projects"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            op.f("fk_contacts_project_id_projects"),
            "projects",
            ["project_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade():
    with op.batch_alter_table("contacts", schema=None) as batch_op:
        batch_op.drop_constraint(
            op.f("fk_contacts_project_id_projects"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            op.f("fk_contacts_project_id_projects"),
            "projects",
            ["project_id"],
            ["id"],
        )
