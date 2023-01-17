from wtforms import EmailField, Form, PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, Length, ValidationError
from zxcvbn import zxcvbn

from .filters import strip_filter


class Account(Form):
    fullname = StringField(
        "Imię i nazwisko",
        validators=[
            InputRequired("Podaj imię i nazwisko"),
            Length(
                min=5,
                max=50,
                message="Długość musi zawierać się w przedziale %(min)d-%(max)d",
            ),
        ],
        filters=[strip_filter],
    )
    email = EmailField("Email", filters=[strip_filter])
    submit = SubmitField("Zapisz")


class ChangePassword(Form):
    password = PasswordField(
        "Nowe hasło",
        validators=[
            InputRequired(),
            Length(min=5, message="Minimalna długość hasła to %(min)d znaków"),
            EqualTo("confirm", message="Hasła muszą pasować"),
        ],
    )
    confirm = PasswordField("Powtórz hasło")
    submit = SubmitField("Zapisz")

    def validate_password(form, field):
        results = zxcvbn(field.data)
        if results["score"] < 3:
            raise ValidationError("Zbyt proste hasło")
