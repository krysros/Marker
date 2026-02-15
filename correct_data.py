import re
import pycountry
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from marker import models
from marker.utils.geo import location
from marker.forms.filters import dash_filter


def main():
    engine = create_engine("sqlite:///marker.sqlite")
    Session = sessionmaker(bind=engine)
    dbsession = Session()

    for company in dbsession.execute(select(models.Company)).scalars():
        if company.street.startswith('ul.'):
            company.street = company.street.removeprefix('ul.').strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        city = dash_filter(company.city)
        match = re.search(r'(\d{2}-\d{3})\s+(.*)', city)

        if match:
            postcode = match.group(1).strip()
            city = match.group(2).strip()
            company.postcode = postcode
            company.city = city
            print(f"Extracted: {postcode} and {city}")
            dbsession.commit()

        match = re.search(r'((.*)\s+\d{2}-\d{3})', city)

        if match:
            city = match.group(1).strip()
            postcode = match.group(2).strip()
            company.postcode = postcode
            company.city = city
            print(f"Extracted: {postcode} and {city}")
            dbsession.commit()


    for company in dbsession.execute(select(models.Company)).scalars():
        if company.latitude is None or company.longitude is None:
            country = pycountry.countries.get(alpha_2=company.country)
            loc = location(street=company.street, city=company.city, country=getattr(country, 'name', ''), postcode=company.postcode)
            if loc is not None:
                company.latitude = loc["lat"]
                company.longitude = loc["lon"]
                print(f"Updated {getattr(company, 'name', '???')} with lat={loc['lat']} and lon={loc['lon']}")
                dbsession.commit()
            else:
                print(f"Could not find location for {getattr(company, 'name', '???')} with address: {getattr(company, 'street', '???')}, {getattr(company, 'city', '???')}, {getattr(country, 'name', '???')}, {getattr(company, 'postcode', '???')}")

    dbsession.close()


if __name__ == "__main__":
    main()
