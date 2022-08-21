from wtforms import Form, StringField, SelectField, DateField, SubmitField
from wtforms.validators import InputRequired, Length, Optional
from .filters import (
    dash_filter,
    strip_filter,
    remove_multiple_spaces,
)
from .select import PROJECT_DELIVERY_METHODS, STAGES, STATES


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
    deadline = DateField("Termin", validators=[Optional()])
    stage = SelectField("Etap", choices=STAGES)
    project_delivery_method = SelectField(
        "Sposób realizacji", choices=PROJECT_DELIVERY_METHODS
    )
    submit = SubmitField("Zapisz")


class ProjectSearchForm(Form):
    name = StringField("Nazwa", filters=[strip_filter])
    street = StringField("Ulica", filters=[strip_filter])
    postcode = StringField("Kod pocztowy", filters=[strip_filter])
    city = StringField("Miasto", filters=[strip_filter])
    state = SelectField("Województwo", choices=STATES)
    link = StringField("Link", filters=[strip_filter])
    deadline = DateField("Termin", validators=[Optional()])
    stage = SelectField("Etap", choices=STAGES)
    project_delivery_method = SelectField(
        "Sposób realizacji", choices=PROJECT_DELIVERY_METHODS
    )
    submit = SubmitField("Szukaj")
