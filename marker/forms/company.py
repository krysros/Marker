from operator import mul
from sqlalchemy import select
from wtforms import Form, StringField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from .filters import (
    dash_filter,
    strip_filter,
    remove_dashes_and_spaces,
    remove_multiple_spaces,
)
from ..models import Company
from .select import COLORS, COUNTRIES, COURTS, STATES


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
        "Nazwa",
        validators=[
            InputRequired("Podaj nazwę"),
            Length(max=100, message="Długość nie może przekraczać %(max)d znaków"),
        ],
        filters=[strip_filter],
    )
    street = StringField(
        "Ulica",
        validators=[
            Length(max=100, message="Długość nie może przekraczać %(max)d znaków")
        ],
        filters=[strip_filter],
    )
    postcode = StringField(
        "Kod pocztowy",
        validators=[
            Length(max=10, message="Długość nie może przekraczać %(max)d znaków")
        ],
        filters=[strip_filter, dash_filter, remove_multiple_spaces],
    )
    city = StringField(
        "Miasto",
        validators=[
            Length(max=100, message="Długość nie może przekraczać %(max)d znaków")
        ],
        filters=[strip_filter],
    )
    state = SelectField("Województwo", choices=STATES)
    country = SelectField("Kraj", choices=COUNTRIES)
    WWW = StringField(
        "WWW",
        validators=[
            Length(max=100, message="Długość nie może przekraczać %(max)d znaków")
        ],
        filters=[strip_filter],
    )
    NIP = StringField(
        "NIP",
        validators=[
            Length(max=20, message="Długość nie może przekraczać %(max)d znaków")
        ],
        filters=[
            strip_filter,
            dash_filter,
            remove_multiple_spaces,
            remove_dashes_and_spaces,
        ],
    )
    REGON = StringField(
        "REGON",
        validators=[
            Length(max=20, message="Długość nie może przekraczać %(max)d znaków")
        ],
        filters=[
            strip_filter,
            dash_filter,
            remove_multiple_spaces,
            remove_dashes_and_spaces,
        ],
    )
    KRS = StringField(
        "KRS",
        validators=[
            Length(max=20, message="Długość nie może przekraczać %(max)d znaków")
        ],
        filters=[
            strip_filter,
            dash_filter,
            remove_multiple_spaces,
            remove_dashes_and_spaces,
        ],
    )
    court = SelectField("Sąd", choices=COURTS)
    color = SelectField("Kolor", choices=COLORS)
    submit = SubmitField("Zapisz")

    def __init__(self, *args, dbsession, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None
        self.dbsession = dbsession

    def validate_name(self, field):
        if self.edited_item:
            if self.edited_item.name == field.data:
                return
        exists = self.dbsession.execute(
            select(Company).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists:
            raise ValidationError("Ta nazwa jest już zajęta")

    def validate_NIP(self, field):
        if not field.data:
            return

        if len(field.data) != 10 or not field.data.isdigit():
            raise ValidationError("Numer NIP powinien się składać z 10 cyfr")

        digits = list(map(int, field.data))
        weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
        check_sum = sum(map(mul, digits[0:9], weights)) % 11
        if check_sum != digits[9]:
            raise ValidationError("Nieprawidłowy numer NIP")

    def validate_REGON(self, field):
        if not field.data:
            return

        if len(field.data) != 9 and len(field.data) != 14 or not field.data.isdigit():
            raise ValidationError("Numer REGON powinien się składać z 9 lub 14 cyfr")
        digits = list(map(int, field.data))

        if len(field.data) == 9:
            valid = _check_sum_9(digits)
        else:
            valid = _check_sum_9(digits) and _check_sum_14(digits)

        if not valid:
            raise ValidationError("Nieprawidłowy numer REGON")

    def validate_KRS(self, field):
        if not field.data:
            return

        if len(field.data) != 10 or not field.data.isdigit():
            raise ValidationError("Numer KRS powinien się składać z 10 cyfr")


class CompanySearchForm(Form):
    name = StringField("Nazwa", filters=[strip_filter])
    street = StringField("Ulica", filters=[strip_filter])
    postcode = StringField("Kod pocztowy", filters=[strip_filter])
    city = StringField("Miasto", filters=[strip_filter])
    state = SelectField("Województwo", choices=STATES)
    country = SelectField("Kraj", choices=COUNTRIES)
    WWW = StringField("WWW", filters=[strip_filter])
    NIP = StringField("NIP", filters=[strip_filter])
    REGON = StringField("REGON", filters=[strip_filter])
    KRS = StringField("KRS", filters=[strip_filter])
    court = SelectField("Sąd", choices=COURTS)
    color = SelectField("Kolor", choices=COLORS)
    submit = SubmitField("Szukaj")
