from wtforms import Form, StringField, SelectField, DateField, SubmitField
from wtforms.validators import InputRequired, Length
from .filters import (
    dash_filter,
    strip_filter,
    remove_multiple_spaces,
)
from marker.forms.select import PROJECT_DELIVERY_METHODS, STAGES, STATES


class ProjectForm(Form):
    name = StringField(
        "Nazwa",
        validators=[
            InputRequired("Podaj nazwę"),
            Length(max=200, message="Długość nie może przekraczać %(max)d znaków"),
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
    link = StringField(
        "Link",
        validators=[
            Length(max=2000, message="Długość nie może przekraczać %(max)d znaków")
        ],
        filters=[strip_filter],
    )
    deadline = DateField("Termin")
    stage = SelectField("Etap", choices=STAGES)
    project_delivery_method = SelectField(
        "Sposób realizacji", choices=PROJECT_DELIVERY_METHODS
    )
    submit = SubmitField("Zapisz")
