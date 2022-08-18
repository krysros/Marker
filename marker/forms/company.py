from operator import mul
from wtforms import Form, StringField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from .filters import (
    dash_filter,
    strip_filter,
    remove_dashes_and_spaces,
    remove_multiple_spaces,
)
from marker.forms.select import COLORS, COURTS, STATES


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
    name = StringField('Nazwa', validators=[InputRequired('Podaj nazwę'), Length(max=100, message='Długość nie może przekraczać %(max)d znaków')], filters=[strip_filter])
    street = StringField('Ulica', validators=[Length(max=100, message='Długość nie może przekraczać %(max)d znaków')], filters=[strip_filter])
    postcode = StringField('Kod pocztowy', validators=[Length(max=10, message='Długość nie może przekraczać %(max)d znaków')], filters=[strip_filter, dash_filter, remove_multiple_spaces])
    city = StringField('Miasto', validators=[Length(max=100, message='Długość nie może przekraczać %(max)d znaków')], filters=[strip_filter])
    state = SelectField('Województwo', choices=STATES)
    WWW = StringField('WWW', validators=[Length(max=100, message='Długość nie może przekraczać %(max)d znaków')], filters=[strip_filter])
    NIP = StringField('NIP', validators=[Length(max=20, message='Długość nie może przekraczać %(max)d znaków')], filters=[strip_filter, dash_filter, remove_multiple_spaces, remove_dashes_and_spaces])
    REGON = StringField('REGON', validators=[Length(max=20, message='Długość nie może przekraczać %(max)d znaków')], filters=[strip_filter, dash_filter, remove_multiple_spaces, remove_dashes_and_spaces])
    KRS = StringField('KRS', validators=[Length(max=20, message='Długość nie może przekraczać %(max)d znaków')], filters=[strip_filter, dash_filter, remove_multiple_spaces, remove_dashes_and_spaces])
    court = SelectField('Sąd', choices=COURTS)
    color = SelectField('Kolor', choices=COLORS)
    submit = SubmitField('Zapisz')

    def validate_NIP(form, field):
        if not field.data:
            return

        if len(field.data) != 10 or not field.data.isdigit():
            raise ValidationError("Numer NIP powinien się składać z 10 cyfr")

        digits = list(map(int, field.data))
        weights = (6, 5, 7, 2, 3, 4, 5, 6, 7)
        check_sum = sum(map(mul, digits[0:9], weights)) % 11
        if check_sum != digits[9]:
            raise ValidationError("Nieprawidłowy numer NIP")

    def validate_REGON(form, field):
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

    def validate_KRS(form, field):
        if not field.data:
            return

        if len(field.data) != 10 or not field.data.isdigit():
            raise ValidationError("Numer KRS powinien się składać z 10 cyfr")
