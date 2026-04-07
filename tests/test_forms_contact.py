from webob.multidict import MultiDict

from marker.forms.contact import ContactForm


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


def make_form(name):
    data = MultiDict({"name": name})
    return ContactForm(request=DummyRequest(), formdata=data)


def test_contact_form_valid_name():
    form = make_form("Jan Kowalski")
    assert form.validate() is True


def test_contact_form_invalid_name_dash():
    form = make_form("---Firma")
    assert not form.validate()
    assert "name" in form.errors
    # Nie sprawdzamy treści komunikatu, tylko obecność błędu


def test_contact_form_invalid_name_only_dash():
    form = make_form("---")
    assert not form.validate()
    assert "name" in form.errors
    # Nie sprawdzamy treści komunikatu, tylko obecność błędu


def test_contact_form_valid_name_digit():
    form = make_form("1Firma")
    assert form.validate() is True


def test_contact_form_valid_name_letter():
    form = make_form("Firma123")
    assert form.validate() is True
