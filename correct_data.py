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
        if 'ul.' in company.street:
            _, street = company.street.split('ul.', maxsplit=1)
            company.street = street.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if 'UL.' in company.street:
            _, street = company.street.split('UL.', maxsplit=1)
            company.street = street.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if company.name.startswith('Sz. P.'):
            company.name = company.name.removeprefix('Sz. P.').strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if 'Sz. P.' in company.name:
            name, _ = company.name.split('Sz. P.', maxsplit=1)
            company.name = name.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if 'sz. P.' in company.name:
            name, _ = company.name.split('sz. P.', maxsplit=1)
            company.name = name.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if 'Sz.P.' in company.name:
            name, _ = company.name.split('Sz.P.', maxsplit=1)
            company.name = name.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if 'Sz. Pani' in company.name:
            name, _ = company.name.split('Sz. Pani', maxsplit=1)
            company.name = name.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if company.name.endswith(','):
            company.name = company.name.removesuffix(',').strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if 'k.' in company.city:
            city, _ = company.city.split('k.', maxsplit=1)
            company.city = city.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if 'K.' in company.city:
            city, _ = company.city.split('K.', maxsplit=1)
            company.city = city.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if 'k,' in company.city:
            city, _ = company.city.split('k,', maxsplit=1)
            company.city = city.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if '/' in company.city:
            city, _ = company.city.split('/', maxsplit=1)
            company.city = city.strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if company.city.startswith('-'):
            company.city = company.city.removeprefix('-').strip()
            dbsession.commit()

    for company in dbsession.execute(select(models.Company)).scalars():
        if re.search(r'\d', company.city):
            cleaned_city = re.sub(r'^\d+\s*', '', company.city)
            company.city = cleaned_city
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
