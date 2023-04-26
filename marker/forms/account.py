from wtforms import EmailField, Form, PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, Length, ValidationError
from zxcvbn import zxcvbn

from .filters import strip_filter
from .ts import TranslationString as _


class Account(Form):
    fullname = StringField(
        _("Fullname"),
        validators=[
            InputRequired(),
            Length(min=5, max=50),
        ],
        filters=[strip_filter],
    )
    email = EmailField(_("Email"), filters=[strip_filter])
    submit = SubmitField(_("Save"))


class ChangePassword(Form):
    password = PasswordField(
        _("New password"),
        validators=[
            InputRequired(),
            Length(min=5),
        ],
    )
    confirm = PasswordField(
        _("Confirm password"),
        validators=[
            EqualTo("password"),
        ],
    )
    submit = SubmitField(_("Save"))

    def validate_password(form, field):
        results = zxcvbn(field.data)
        if results["score"] < 3:
            raise ValidationError(_("The password is too simple"))
