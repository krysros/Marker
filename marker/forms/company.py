from operator import mul

from sqlalchemy import select
from wtforms import Form, HiddenField, SelectField, SelectMultipleField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

from ..models import Company
from .association import ActivityForm
from .filters import (
    dash_filter,
    remove_dashes_and_spaces,
    remove_multiple_spaces,
    strip_filter,
    title,
)
from .select import COLORS, COURTS, select_countries, select_subdivisions
from .ts import TranslationString as _


def _check_sum_9(digits):
    weights9 = (8, 9, 2, 3, 4, 5, 6, 7)
    check_sum = sum(map(mul, digits[0:8], weights9)) % 11
    if check_sum == 10:
        check_sum = 0
    if check_sum == digits[8]:
        return True
    else:
        return False


def _check_sum_14(digits):
    weights14 = (2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8)
    check_sum = sum(map(mul, digits[0:13], weights14)) % 11
    if check_sum == 10:
        check_sum = 0
    if check_sum == digits[13]:
        return True
    else:
        return False


class CompanyForm(Form):
    name = StringField(
        _("Name"),
        validators=[
            InputRequired(),
            Length(max=100),
        ],
        filters=[strip_filter],
    )
    street = StringField(
        _("Street"),
        validators=[Length(max=100)],
        filters=[strip_filter],
    )
    postcode = StringField(
        _("Post code"),
        validators=[Length(max=10)],
        filters=[strip_filter, dash_filter, remove_multiple_spaces],
    )
    city = StringField(
        _("City"),
        validators=[Length(max=100)],
        filters=[strip_filter, title],
    )
    subdivision = SelectField(
        _("Subdivision"), choices=select_subdivisions(), validate_choice=False
    )
    country = SelectField(_("Country"), choices=select_countries())
    website = StringField(
        _("Website"),
        validators=[Length(max=100)],
        filters=[strip_filter],
    )
    color = SelectField(_("Color"), choices=COLORS, default="")
    NIP = StringField(
        _("NIP"),
        validators=[Length(max=20)],
        filters=[
            strip_filter,
            dash_filter,
            remove_multiple_spaces,
            remove_dashes_and_spaces,
        ],
    )
    REGON = StringField(
        _("REGON"),
        validators=[Length(max=20)],
        filters=[
            strip_filter,
            dash_filter,
            remove_multiple_spaces,
            remove_dashes_and_spaces,
        ],
    )
    KRS = StringField(
        _("KRS"),
        validators=[Length(max=20)],
        filters=[
            strip_filter,
            dash_filter,
            remove_multiple_spaces,
            remove_dashes_and_spaces,
        ],
    )
    court = SelectField(_("Court"), choices=COURTS)

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None

        try:
            country = self.edited_item.country
        except AttributeError:
            country = None

        self.subdivision.choices = select_subdivisions(country)

    def validate_name(self, field):
        if self.edited_item:
            if self.edited_item.name == field.data:
                return
        exists = self.request.dbsession.execute(
            select(Company).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists:
            raise ValidationError(_("This name is already taken"))

    def validate_NIP(self, field):
        if not field.data:
            return

        if len(field.data) != 10 or not field.data.isdigit():
            raise ValidationError(_("The NIP number should consist of 10 digits"))

        digits = list(map(int, field.data))
        weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
        check_sum = sum(map(mul, digits[0:9], weights)) % 11
        if check_sum != digits[9]:
            raise ValidationError(_("Invalid VAT number"))

    def validate_REGON(self, field):
        if not field.data:
            return

        if len(field.data) != 9 and len(field.data) != 14 or not field.data.isdigit():
            raise ValidationError(
                _("The REGON number should consist of 9 or 14 digits")
            )
        digits = list(map(int, field.data))

        if len(field.data) == 9:
            valid = _check_sum_9(digits)
        else:
            valid = _check_sum_9(digits) and _check_sum_14(digits)

        if not valid:
            raise ValidationError(_("Invalid REGON number"))

    def validate_KRS(self, field):
        if not field.data:
            return

        if len(field.data) != 10 or not field.data.isdigit():
            raise ValidationError(_("The KRS number should consist of 10 digits"))


class CompanySearchForm(Form):
    name = StringField(_("Name"), filters=[strip_filter])
    street = StringField(_("Street"), filters=[strip_filter])
    postcode = StringField(_("Post code"), filters=[strip_filter])
    city = StringField(_("City"), filters=[strip_filter])
    subdivision = SelectField(
        _("Subdivision"), choices=select_subdivisions(), validate_choice=False
    )
    country = SelectField(_("Country"), choices=select_countries())
    website = StringField(_("Website"), filters=[strip_filter])
    color = SelectField(_("Color"), choices=COLORS)
    NIP = StringField(_("NIP"), filters=[strip_filter])
    REGON = StringField(_("REGON"), filters=[strip_filter])
    KRS = StringField(_("KRS"), filters=[strip_filter])
    court = SelectField(_("Court"), choices=COURTS)


class CompanyFilterForm(Form):
    name = HiddenField(_("Name"), filters=[strip_filter])
    street = HiddenField(_("Street"), filters=[strip_filter])
    postcode = HiddenField(_("Post code"), filters=[strip_filter])
    city = HiddenField(_("City"), filters=[strip_filter])
    subdivision = SelectMultipleField(
        _("Subdivision"), choices=select_subdivisions(), validate_choice=False
    )
    country = SelectField(_("Country"), choices=select_countries())
    website = HiddenField(_("Website"), filters=[strip_filter])
    color = SelectField(_("Color"), choices=COLORS)
    NIP = StringField(_("NIP"), filters=[strip_filter])
    REGON = StringField(_("REGON"), filters=[strip_filter])
    KRS = StringField(_("KRS"), filters=[strip_filter])
    court = SelectField(_("Court"), choices=COURTS)

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None

        try:
            country = self.edited_item.country
        except AttributeError:
            country = None

        self.subdivision.choices = select_subdivisions(country)
        self.subdivision.default = self.request.GET.getall("subdivision")


class CompanyActivityForm(ActivityForm):
    name = StringField(_("Name"), validators=[InputRequired()])

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None

    def validate_name(self, field):
        if self.edited_item:
            if self.edited_item.name == field.data:
                return
        exists = self.request.dbsession.execute(
            select(Company).filter_by(name=field.data)
        ).scalar_one_or_none()
        if not exists:
            raise ValidationError(_("There is no company with this name"))
