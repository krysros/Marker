from sqlalchemy import select
from wtforms import (
    EmailField,
    Form,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import InputRequired, Length, ValidationError
from zxcvbn import zxcvbn

from ..models import User
from .filters import strip_filter
from .select import USER_ROLES


class UserForm(Form):
    name = StringField(
        "Nazwa",
        validators=[
            InputRequired("Podaj nazwę użytkownika"),
            Length(
                min=3,
                max=30,
                message="Długość musi zawierać się w przedziale %(min)d-%(max)d",
            ),
        ],
        filters=[strip_filter],
    )
    fullname = StringField(
        "Imię i nazwisko",
        validators=[
            InputRequired("Podaj imię i nazwisko"),
            Length(
                min=3,
                max=50,
                message="Długość musi zawierać się w przedziale %(min)d-%(max)d",
            ),
        ],
        filters=[strip_filter],
    )
    email = EmailField("Email", validators=[InputRequired()], filters=[strip_filter])
    role = SelectField("Rola", validators=[InputRequired()], choices=USER_ROLES)
    password = PasswordField(
        "Hasło",
        validators=[
            InputRequired(),
            Length(min=5, message="Minimalna długość hasła to %(min)d znaków"),
        ],
    )
    submit = SubmitField("Zapisz")

    def __init__(self, *args, request, username=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.username = username

    def validate_name(self, field):
        exists = self.request.dbsession.execute(
            select(User).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists and self.username != exists.name:
            raise ValidationError("Ta nazwa jest już zajęta")

    def validate_password(form, field):
        results = zxcvbn(field.data)
        if results["score"] < 3:
            raise ValidationError("Zbyt proste hasło")


class UserSearchForm(Form):
    name = StringField("Nazwa", filters=[strip_filter])
    fullname = StringField("Imię i nazwisko", filters=[strip_filter])
    email = StringField("Email", filters=[strip_filter])
    role = SelectField("Rola", choices=USER_ROLES)
    submit = SubmitField("Szukaj")
