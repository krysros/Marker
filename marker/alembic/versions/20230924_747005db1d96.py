"""Copy identification numbers

Revision ID: 747005db1d96
Revises: 965c3826a7aa
Create Date: 2023-09-24 23:29:17.054480

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm.session import Session

from marker.models import Company, IdentificationNumber

# revision identifiers, used by Alembic.
revision = "747005db1d96"
down_revision = "965c3826a7aa"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    companies = session.execute(sa.select(Company)).scalars()
    for company in companies:
        id_num = IdentificationNumber(
            NIP=company.NIP, REGON=company.REGON, KRS=company.KRS, sad=company.court
        )
        company.identification_number = id_num
    session.commit()


def downgrade():
    pass
