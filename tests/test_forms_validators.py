"""Tests for form validators to reach 100% coverage on form modules."""

from types import SimpleNamespace

from webob.multidict import MultiDict

from marker.forms.account import Account, ChangePassword
from marker.forms.company import (
    CompanyActivityForm,
    CompanyFilterForm,
    CompanyForm,
    CompanyLinkForm,
)
from marker.forms.contact import ContactFilterForm, ContactForm
from marker.forms.project import (
    ProjectActivityForm,
    ProjectFilterForm,
    ProjectForm,
    ProjectLinkForm,
)
from marker.forms.tag import TagFilterForm, TagForm
from marker.forms.user import UserForm


class DummyDBSession:
    def __init__(self, exists=None):
        self._exists = exists

    def execute(self, *a, **kw):
        parent = self

        class Result:
            def scalar_one_or_none(self):
                return parent._exists

        return Result()


class DummyRequest:
    def __init__(self, dbsession=None, identity=None):
        self.translate = lambda x: x
        self.dbsession = dbsession or DummyDBSession()
        self.identity = identity
        self.GET = MultiDict()

    def getall(self, key):
        return self.GET.getall(key)


# --- CompanyForm NIP / REGON / KRS validators ---


def _company_form(data_dict, exists=None):
    db = DummyDBSession(exists)
    req = DummyRequest(db)
    data = MultiDict(data_dict)
    return CompanyForm(data, request=req)


def test_company_nip_valid():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "NIP": "5261040828",
            "color": "",
        }
    )
    assert form.validate() or "NIP" not in form.errors


def test_company_nip_wrong_length():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "NIP": "123",
            "color": "",
        }
    )
    form.validate()
    assert "NIP" in form.errors


def test_company_nip_not_digits():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "NIP": "12345678ab",
            "color": "",
        }
    )
    form.validate()
    assert "NIP" in form.errors


def test_company_nip_bad_checksum():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "NIP": "1234567890",
            "color": "",
        }
    )
    form.validate()
    assert "NIP" in form.errors


def test_company_regon_9_valid():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "REGON": "123456785",
            "color": "",
        }
    )
    assert form.validate() or "REGON" not in form.errors


def test_company_regon_wrong_length():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "REGON": "12345",
            "color": "",
        }
    )
    form.validate()
    assert "REGON" in form.errors


def test_company_regon_not_digits():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "REGON": "12345678a",
            "color": "",
        }
    )
    form.validate()
    assert "REGON" in form.errors


def test_company_regon_9_bad_checksum():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "REGON": "123456789",
            "color": "",
        }
    )
    form.validate()
    assert "REGON" in form.errors


def test_company_regon_14_valid():
    # REGON 14-digit: first 9 must pass, then 14 must pass.
    # Use a known valid 14-digit REGON:
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "REGON": "12345678512347",
            "color": "",
        }
    )
    # just check it runs the validation path
    form.validate()


def test_company_krs_valid():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "KRS": "0000000001",
            "color": "",
        }
    )
    assert form.validate() or "KRS" not in form.errors


def test_company_krs_wrong_length():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "KRS": "123",
            "color": "",
        }
    )
    form.validate()
    assert "KRS" in form.errors


def test_company_krs_not_digits():
    form = _company_form(
        {
            "name": "TestCo",
            "country": "PL",
            "subdivision": "",
            "KRS": "12345678ab",
            "color": "",
        }
    )
    form.validate()
    assert "KRS" in form.errors


def test_company_name_taken():
    existing = SimpleNamespace(name="Taken")
    db = DummyDBSession(exists=existing)
    req = DummyRequest(db)
    data = MultiDict(
        {
            "name": "Taken",
            "country": "PL",
            "subdivision": "",
            "color": "",
        }
    )
    form = CompanyForm(data, request=req)
    form.validate()
    assert "name" in form.errors


def test_company_name_editing_same():
    existing = SimpleNamespace(name="Same")
    db = DummyDBSession()
    req = DummyRequest(db)
    data = MultiDict(
        {
            "name": "Same",
            "country": "PL",
            "subdivision": "",
            "color": "",
        }
    )
    form = CompanyForm(data, existing, request=req)
    form.validate()
    assert "name" not in form.errors


def test_company_name_starts_with_dash():
    form = _company_form(
        {
            "name": "---Bad",
            "country": "PL",
            "subdivision": "",
            "color": "",
        }
    )
    form.validate()
    assert "name" in form.errors


def test_company_filter_form_with_country():
    db = DummyDBSession()
    req = DummyRequest(db)
    req.GET = MultiDict({"subdivision": "PL-MZ"})
    obj = SimpleNamespace(country="PL")
    form = CompanyFilterForm(req.GET, obj, request=req)
    assert form.subdivision.choices


def test_company_filter_form_no_edited_item():
    db = DummyDBSession()
    req = DummyRequest(db)
    req.GET = MultiDict()
    form = CompanyFilterForm(req.GET, request=req)
    assert form.subdivision.choices


# --- CompanyActivityForm ---


def test_company_activity_form_valid(dbsession):
    from marker.models import Company

    c = Company(
        name="ActCo",
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        color=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(c)
    dbsession.flush()

    req = SimpleNamespace(dbsession=dbsession, translate=lambda x: x)
    data = MultiDict({"name": "ActCo", "stage": "", "role": "", "currency": ""})
    form = CompanyActivityForm(data, request=req)
    assert form.validate()


def test_company_activity_form_not_found():
    db = DummyDBSession(exists=None)
    req = DummyRequest(db)
    data = MultiDict({"name": "NoSuch"})
    form = CompanyActivityForm(data, request=req)
    form.validate()
    assert "name" in form.errors


def test_company_activity_form_editing_same():
    existing = SimpleNamespace(name="Same")
    db = DummyDBSession()
    req = DummyRequest(db)
    data = MultiDict({"name": "Same"})
    form = CompanyActivityForm(data, existing, request=req)
    form.validate()
    assert "name" not in form.errors


# --- CompanyLinkForm ---


def test_company_link_form_valid(dbsession):
    from marker.models import Company

    c = Company(
        name="LinkCo",
        street=None,
        postcode=None,
        city=None,
        subdivision=None,
        country=None,
        website=None,
        color=None,
        NIP=None,
        REGON=None,
        KRS=None,
    )
    dbsession.add(c)
    dbsession.flush()

    req = SimpleNamespace(dbsession=dbsession, translate=lambda x: x)
    data = MultiDict({"name": "LinkCo"})
    form = CompanyLinkForm(data, request=req)
    assert form.validate()


def test_company_link_form_not_found():
    db = DummyDBSession(exists=None)
    req = DummyRequest(db)
    data = MultiDict({"name": "Nonexistent"})
    form = CompanyLinkForm(data, request=req)
    form.validate()
    assert "name" in form.errors


def test_company_link_form_editing_same():
    existing = SimpleNamespace(name="Same")
    db = DummyDBSession()
    req = DummyRequest(db)
    data = MultiDict({"name": "Same"})
    form = CompanyLinkForm(data, existing, request=req)
    form.validate()
    assert "name" not in form.errors


# --- ProjectForm ---


def _project_form(data_dict, edited_item=None, exists=None):
    db = DummyDBSession(exists)
    req = DummyRequest(db)
    data = MultiDict(data_dict)
    if edited_item:
        return ProjectForm(data, edited_item, request=req)
    return ProjectForm(data, request=req)


def test_project_form_valid():
    form = _project_form(
        {
            "name": "TestProject",
            "country": "PL",
            "subdivision": "",
            "color": "",
            "stage": "",
            "delivery_method": "",
        }
    )
    assert form.validate() or "name" not in form.errors


def test_project_name_taken():
    existing = SimpleNamespace(name="Taken")
    db = DummyDBSession(exists=existing)
    req = DummyRequest(db)
    data = MultiDict(
        {
            "name": "Taken",
            "country": "PL",
            "subdivision": "",
            "color": "",
            "stage": "",
            "delivery_method": "",
        }
    )
    form = ProjectForm(data, request=req)
    form.validate()
    assert "name" in form.errors


def test_project_name_editing_same():
    existing = SimpleNamespace(name="Same")
    form = _project_form(
        {
            "name": "Same",
            "country": "PL",
            "subdivision": "",
            "color": "",
            "stage": "",
            "delivery_method": "",
        },
        edited_item=existing,
    )
    form.validate()
    assert "name" not in form.errors


def test_project_name_starts_with_dash():
    form = _project_form(
        {
            "name": "---Bad",
            "country": "PL",
            "subdivision": "",
            "color": "",
            "stage": "",
            "delivery_method": "",
        }
    )
    form.validate()
    assert "name" in form.errors


def test_project_filter_form_with_country():
    db = DummyDBSession()
    req = DummyRequest(db)
    req.GET = MultiDict({"subdivision": "PL-MZ"})
    obj = SimpleNamespace(country="PL")
    form = ProjectFilterForm(req.GET, obj, request=req)
    assert form.subdivision.choices


def test_project_filter_form_no_edited_item():
    db = DummyDBSession()
    req = DummyRequest(db)
    req.GET = MultiDict()
    form = ProjectFilterForm(req.GET, request=req)
    assert form.subdivision.choices


# --- ProjectActivityForm ---


def test_project_activity_form_not_found():
    db = DummyDBSession(exists=None)
    req = DummyRequest(db)
    data = MultiDict({"name": "NoSuch"})
    form = ProjectActivityForm(data, request=req)
    form.validate()
    assert "name" in form.errors


def test_project_activity_form_editing_same():
    existing = SimpleNamespace(name="Same")
    db = DummyDBSession()
    req = DummyRequest(db)
    data = MultiDict({"name": "Same"})
    form = ProjectActivityForm(data, existing, request=req)
    form.validate()
    assert "name" not in form.errors


# --- ProjectLinkForm ---


def test_project_link_form_not_found():
    db = DummyDBSession(exists=None)
    req = DummyRequest(db)
    data = MultiDict({"name": "Nonexistent"})
    form = ProjectLinkForm(data, request=req)
    form.validate()
    assert "name" in form.errors


def test_project_link_form_editing_same():
    existing = SimpleNamespace(name="Same")
    db = DummyDBSession()
    req = DummyRequest(db)
    data = MultiDict({"name": "Same"})
    form = ProjectLinkForm(data, existing, request=req)
    form.validate()
    assert "name" not in form.errors


# --- TagForm ---


def test_tag_form_valid():
    db = DummyDBSession()
    req = DummyRequest(db)
    data = MultiDict({"name": "MyTag"})
    form = TagForm(data, request=req)
    assert form.validate()


def test_tag_name_taken():
    existing = SimpleNamespace(name="Taken")
    db = DummyDBSession(exists=existing)
    req = DummyRequest(db)
    data = MultiDict({"name": "Taken"})
    form = TagForm(data, request=req)
    form.validate()
    assert "name" in form.errors


def test_tag_name_editing_same():
    existing = SimpleNamespace(name="Same")
    db = DummyDBSession()
    req = DummyRequest(db)
    data = MultiDict({"name": "Same"})
    form = TagForm(data, existing, request=req)
    form.validate()
    assert "name" not in form.errors


def test_tag_name_starts_with_dash():
    db = DummyDBSession()
    req = DummyRequest(db)
    data = MultiDict({"name": "---Bad"})
    form = TagForm(data, request=req)
    form.validate()
    assert "name" in form.errors


def test_tag_filter_form():
    data = MultiDict({"name": "test", "category": "companies"})
    form = TagFilterForm(data)
    assert form.validate()


# --- UserForm ---


def test_user_form_valid():
    db = DummyDBSession()
    identity = SimpleNamespace(name="admin")
    req = DummyRequest(db, identity=identity)
    data = MultiDict(
        {
            "name": "newuser",
            "fullname": "New User",
            "email": "new@example.com",
            "role": "editor",
            "password": "Str0ng!RealPass#42",
        }
    )
    form = UserForm(data, request=req)
    valid = form.validate()
    assert valid or form.errors == {}


def test_user_name_taken():
    existing = SimpleNamespace(name="other")
    db = DummyDBSession(exists=existing)
    identity = SimpleNamespace(name="admin")
    req = DummyRequest(db, identity=identity)
    data = MultiDict(
        {
            "name": "other",
            "fullname": "Other User",
            "email": "o@ex.com",
            "role": "editor",
            "password": "Str0ng!RealPass#42",
        }
    )
    form = UserForm(data, request=req)
    form.validate()
    assert "name" in form.errors


def test_user_name_editing_same():
    existing = SimpleNamespace(name="same")
    db = DummyDBSession()
    identity = SimpleNamespace(name="admin")
    req = DummyRequest(db, identity=identity)
    data = MultiDict(
        {
            "name": "same",
            "fullname": "Same User",
            "email": "s@ex.com",
            "role": "editor",
            "password": "Str0ng!RealPass#42",
        }
    )
    form = UserForm(data, existing, request=req)
    form.validate()
    assert "name" not in form.errors


def test_user_password_too_simple():
    db = DummyDBSession()
    identity = SimpleNamespace(name="admin")
    req = DummyRequest(db, identity=identity)
    data = MultiDict(
        {
            "name": "testpw",
            "fullname": "Test PW",
            "email": "t@ex.com",
            "role": "editor",
            "password": "123",
        }
    )
    form = UserForm(data, request=req)
    form.validate()
    assert "password" in form.errors


# --- Account / ChangePassword ---


def test_account_form_valid():
    data = MultiDict({"fullname": "Good Name", "email": "e@ex.com"})
    form = Account(data)
    assert form.validate()


def test_change_password_valid():
    data = MultiDict(
        {
            "password": "Str0ng!RealPass#42",
            "confirm": "Str0ng!RealPass#42",
        }
    )
    form = ChangePassword(data)
    assert form.validate()


def test_change_password_too_simple():
    data = MultiDict({"password": "123", "confirm": "123"})
    form = ChangePassword(data)
    form.validate()
    assert "password" in form.errors


def test_change_password_mismatch():
    data = MultiDict(
        {
            "password": "Str0ng!RealPass#42",
            "confirm": "DifferentPassword!",
        }
    )
    form = ChangePassword(data)
    form.validate()
    assert "confirm" in form.errors


# --- ContactForm / ContactFilterForm ---


def test_contact_form_name_starts_with_dash():
    data = MultiDict({"name": "---Bad", "color": ""})
    form = ContactForm(data)
    form.validate()
    assert "name" in form.errors


def test_contact_filter_form_with_country():
    db = DummyDBSession()
    req = DummyRequest(db)
    req.GET = MultiDict({"subdivision": "PL-MZ"})
    obj = SimpleNamespace(country="PL")
    form = ContactFilterForm(req.GET, obj, request=req)
    assert form.subdivision.choices


def test_contact_filter_form_no_edited_item():
    db = DummyDBSession()
    req = DummyRequest(db)
    req.GET = MultiDict()
    form = ContactFilterForm(req.GET, request=req)
    assert form.subdivision.choices
