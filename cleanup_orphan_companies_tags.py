import argparse
import sys

from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import delete, exists, func, or_, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from marker import models
from marker.models import Company, Tag, companies_tags


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_uri",
        help="Configuration file, e.g., development.ini",
    )
    return parser.parse_args(argv[1:])


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    settings = get_appsettings(args.config_uri)
    engine = models.get_engine(settings)

    try:
        with Session(engine) as dbsession:

            company_missing = ~exists(
                select(1).where(Company.id == companies_tags.c.company_id)
            )
            tag_missing = ~exists(
                select(1).where(Tag.id == companies_tags.c.tag_id)
            )
            orphan_condition = or_(company_missing, tag_missing)

            stmt = (
                select(companies_tags.c.company_id, companies_tags.c.tag_id)
                .where(orphan_condition)
                .order_by(companies_tags.c.company_id, companies_tags.c.tag_id)
            )
            rows = dbsession.execute(stmt).all()

            if not rows:
                print("No orphan records found in companies_tags table.")
                return

            print("Removing orphan records from companies_tags (company_id, tag_id):")
            for company_id, tag_id in rows:
                print(f"{company_id}, {tag_id}")

            orphan_pairs = {(company_id, tag_id) for company_id, tag_id in rows}
            deleted_rows = 0

            for company_id, tag_id in orphan_pairs:
                delete_stmt = delete(companies_tags).where(
                    companies_tags.c.company_id == company_id,
                    companies_tags.c.tag_id == tag_id,
                )
                result = dbsession.execute(delete_stmt)
                deleted_rows += result.rowcount or 0

            remaining_orphans = dbsession.scalar(
                select(func.count()).select_from(companies_tags).where(orphan_condition)
            )
            print(f"Deleted records: {deleted_rows}")
            print(f"Remaining orphan records: {remaining_orphans}")
            dbsession.commit()
    except OperationalError:
        print(
            """
Pyramid has a problem with your SQL database.

1. You may need to run alembic migrations.
2. The database server configured in your .ini file may be unavailable.
            """
        )


if __name__ == "__main__":
    main()
