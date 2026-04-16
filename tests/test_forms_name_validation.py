from webob.multidict import MultiDict

from marker.forms.company import CompanyForm
from marker.forms.project import ProjectForm
from marker.forms.tag import TagForm


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


def make_company_form(name):
    data = MultiDict(
        {"name": name, "country": "PL", "subdivision": "PL-MZ", "color": "primary"}
    )
    return CompanyForm(request=DummyRequest(), formdata=data)


def make_project_form(name):
    data = MultiDict(
        {
            "name": name,
            "country": "PL",
            "subdivision": "PL-MZ",
            "color": "primary",
            "stage": "announcement",
            "delivery_method": "design-build",
        }
    )
    return ProjectForm(request=DummyRequest(), formdata=data)


def make_tag_form(name):
    data = MultiDict({"name": name})
    return TagForm(request=DummyRequest(), formdata=data)


def test_company_form_valid_name():
    form = make_company_form("Firma123")
    assert form.validate() is True


def test_company_form_invalid_name_dash():
    form = make_company_form("---Firma")
    assert not form.validate()
    assert "name" in form.errors


def test_company_form_invalid_name_only_dash():
    form = make_company_form("---")
    assert not form.validate()
    assert "name" in form.errors


def test_company_form_valid_name_digit():
    form = make_company_form("1Firma")
    assert form.validate() is True


def test_company_form_valid_name_polish_letter():
    form = make_company_form("ŁódzkaFirma")
    assert form.validate() is True


def test_project_form_valid_name():
    form = make_project_form("Projekt123")
    assert form.validate() is True


def test_project_form_invalid_name_dash():
    form = make_project_form("---Projekt")
    assert not form.validate()
    assert "name" in form.errors


def test_project_form_invalid_name_only_dash():
    form = make_project_form("---")
    assert not form.validate()
    assert "name" in form.errors


def test_project_form_valid_name_digit():
    form = make_project_form("1Projekt")
    assert form.validate() is True


def test_project_form_valid_name_polish_letter():
    form = make_project_form("ŚląskiProjekt")
    assert form.validate() is True


def test_tag_form_valid_name():
    form = make_tag_form("Tag123")
    assert form.validate() is True


def test_tag_form_invalid_name_dash():
    form = make_tag_form("---Tag")
    assert not form.validate()
    assert "name" in form.errors


def test_tag_form_invalid_name_only_dash():
    form = make_tag_form("---")
    assert not form.validate()
    assert "name" in form.errors


def test_tag_form_valid_name_digit():
    form = make_tag_form("1Tag")
    assert form.validate() is True
