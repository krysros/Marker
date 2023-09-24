from operator import mul

from wtforms import Form, HiddenField, SelectField, StringField
from wtforms.validators import Length, ValidationError

from .filters import (
    dash_filter,
    remove_dashes_and_spaces,
    remove_multiple_spaces,
    strip_filter,
)
from .select import COURTS
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


class IdentificationNumberForm(Form):
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
    sad = SelectField(_("Court"), choices=COURTS)

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None

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


class IdentificationNumberSearchForm(Form):
    NIP = StringField(_("NIP"), filters=[strip_filter])
    REGON = StringField(_("REGON"), filters=[strip_filter])
    KRS = StringField(_("KRS"), filters=[strip_filter])
    sad = SelectField(_("Court"), choices=COURTS)


class IdentificationNumberFilterForm(Form):
    NIP = HiddenField(_("NIP"), filters=[strip_filter])
    REGON = HiddenField(_("REGON"), filters=[strip_filter])
    KRS = HiddenField(_("KRS"), filters=[strip_filter])
    sad = HiddenField(_("Court"))

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None
