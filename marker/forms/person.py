from wtforms import Form, StringField, EmailField, SubmitField
from wtforms.validators import InputRequired, Length
from .filters import strip_filter


class PersonForm(Form):
    name = StringField(
        "Imię i nazwisko",
        validators=[
            InputRequired("Podaj imię i nazwisko"),
            Length(
                min=5,
                max=100,
                message="Długość musi zawierać się w przedziale %(min)d-%(max)d",
            ),
        ],
        filters=[strip_filter],
    )
    position = StringField(
        "Stanowisko",
        validators=[
            Length(max=100, message="Długość nie może przekraczać %(max)d znaków"),
        ],
        filters=[strip_filter],
    )
    phone = StringField(
        "Telefon",
        validators=[
            Length(max=50, message="Długość nie może przekraczać %(max)d znaków"),
        ],
        filters=[strip_filter],
    )
    email = EmailField(
        "Email",
        validators=[
            Length(max=50, message="Długość nie może przekraczać %(max)d znaków"),
        ],
        filters=[strip_filter],
    )
    submit = SubmitField("Zapisz")


class PersonSearchForm(Form):
    name = StringField("Imię i nazwisko", filters=[strip_filter])
    position = StringField("Stanowisko", filters=[strip_filter])
    phone = StringField("Telefon", filters=[strip_filter])
    email = EmailField("Email", filters=[strip_filter])
    submit = SubmitField("Szukaj")