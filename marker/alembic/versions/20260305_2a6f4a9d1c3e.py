"""Set ON DELETE CASCADE on contacts.company_id

Revision ID: 2a6f4a9d1c3e
Revises: 7f2b2cf8f4b1
Create Date: 2026-03-05 12:30:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "2a6f4a9d1c3e"
down_revision = "7f2b2cf8f4b1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("contacts", schema=None) as batch_op:
        batch_op.drop_constraint(
            op.f("fk_contacts_company_id_companies"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            op.f("fk_contacts_company_id_companies"),
            "companies",
            ["company_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade():
    with op.batch_alter_table("contacts", schema=None) as batch_op:
        batch_op.drop_constraint(
            op.f("fk_contacts_company_id_companies"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            op.f("fk_contacts_company_id_companies"),
            "companies",
            ["company_id"],
            ["id"],
        )
