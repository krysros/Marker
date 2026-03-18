from marker.forms.company import CompanyForm


def test_company_form_valid():
    class DummyDBSession:
        def execute(self, *a, **kw):
            class Result:
                def scalar_one_or_none(self):
                    return None

            return Result()

    class DummyRequest:
        def __init__(self):
            self.translate = lambda x: x
            self.dbsession = DummyDBSession()

    from werkzeug.datastructures import MultiDict

    data = MultiDict(
        {
            "name": "Test Company",
            "street": "Test Street",
            "postcode": "00-001",
            "city": "Warsaw",
            "subdivision": "PL-MZ",  # valid subdivision code for Poland
            "country": "PL",  # valid country code for Poland
            "website": "",
            "color": "primary",  # valid color from COLORS
            "NIP": "",
            "REGON": "",
            "KRS": "",
            "court": "Białystok XII",  # valid court from COURTS
        }
    )
    form = CompanyForm(request=DummyRequest(), formdata=data)
    from marker.forms.select import (
        COLORS,
        COURTS,
        select_countries,
        select_subdivisions,
    )

    form.subdivision.choices = select_subdivisions("PL")
    form.country.choices = select_countries()
    form.color.choices = COLORS
    form.court.choices = COURTS
    form.process(data=data)
    valid = form.validate()
    if not valid:
        print("form.errors:", form.errors)
    assert valid is True


def test_company_form_missing_name():
    class DummyDBSession:
        def execute(self, *a, **kw):
            class Result:
                def scalar_one_or_none(self):
                    return None

            return Result()

    class DummyRequest:
        def __init__(self):
            self.translate = lambda x: x
            self.dbsession = DummyDBSession()

    from werkzeug.datastructures import MultiDict

    data = MultiDict(
        {
            "street": "Test Street",
            "postcode": "00-001",
            "city": "Warsaw",
            "subdivision": "PL-MZ",
            "country": "PL",
            "website": "",
            "color": "primary",
            "NIP": "",
            "REGON": "",
            "KRS": "",
            "court": "Białystok XII",
        }
    )
    form = CompanyForm(request=DummyRequest(), formdata=data)
    from marker.forms.select import (
        COLORS,
        COURTS,
        select_countries,
        select_subdivisions,
    )

    form.subdivision.choices = select_subdivisions("PL")
    form.country.choices = select_countries()
    form.color.choices = COLORS
    form.court.choices = COURTS
    form.process(data=data)
    assert not form.validate()
    assert "name" in form.errors


def test_company_form_long_name():
    class DummyDBSession:
        def execute(self, *a, **kw):
            class Result:
                def scalar_one_or_none(self):
                    return None

            return Result()

    class DummyRequest:
        def __init__(self):
            self.translate = lambda x: x
            self.dbsession = DummyDBSession()

    from werkzeug.datastructures import MultiDict

    data = MultiDict(
        {
            "name": "A" * 101,
            "street": "Test Street",
            "postcode": "00-001",
            "city": "Warsaw",
            "subdivision": "PL-MZ",
            "country": "PL",
            "website": "",
            "color": "primary",
            "NIP": "",
            "REGON": "",
            "KRS": "",
            "court": "Białystok XII",
        }
    )
    form = CompanyForm(request=DummyRequest(), formdata=data)
    from marker.forms.select import (
        COLORS,
        COURTS,
        select_countries,
        select_subdivisions,
    )

    form.subdivision.choices = select_subdivisions("PL")
    form.country.choices = select_countries()
    form.color.choices = COLORS
    form.court.choices = COURTS
    form.process(data=data)
    assert not form.validate()
    assert "name" in form.errors


def test_company_form_postcode_filters():
    class DummyDBSession:
        def execute(self, *a, **kw):
            class Result:
                def scalar_one_or_none(self):
                    return None

            return Result()

    class DummyRequest:
        def __init__(self):
            self.translate = lambda x: x
            self.dbsession = DummyDBSession()

    from werkzeug.datastructures import MultiDict

    data = MultiDict(
        {
            "name": "Test",
            "street": "Test",
            "postcode": " 00-001  ",
            "city": "Warsaw",
            "subdivision": "PL-MZ",
            "country": "PL",
            "website": "",
            "color": "primary",
            "NIP": "",
            "REGON": "",
            "KRS": "",
            "court": "Białystok XII",
        }
    )
    form = CompanyForm(request=DummyRequest(), formdata=data)
    from marker.forms.select import (
        COLORS,
        COURTS,
        select_countries,
        select_subdivisions,
    )

    form.subdivision.choices = select_subdivisions("PL")
    form.country.choices = select_countries()
    form.color.choices = COLORS
    form.court.choices = COURTS
    form.process(data=data)
    form.validate()
    assert form.postcode.data == "00-001"
