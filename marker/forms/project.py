from sqlalchemy import select
from wtforms import Form, StringField, SelectField, DateField, SubmitField
from wtforms.validators import InputRequired, Length, Optional, ValidationError
from .filters import (
    dash_filter,
    strip_filter,
    remove_multiple_spaces,
)
from ..models import Project
from .select import COUNTRIES, PROJECT_DELIVERY_METHODS, STAGES, STATES, COLORS


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
    country = SelectField("Kraj", choices=COUNTRIES)
    link = StringField(
        "Link",
        validators=[
            Length(max=2000, message="Długość nie może przekraczać %(max)d znaków")
        ],
        filters=[strip_filter],
    )
    color = SelectField("Kolor", choices=COLORS)
    deadline = DateField("Termin", validators=[Optional()])
    stage = SelectField("Etap", choices=STAGES)
    project_delivery_method = SelectField(
        "Sposób realizacji", choices=PROJECT_DELIVERY_METHODS
    )
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
            select(Project).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists:
            raise ValidationError("Ta nazwa jest już zajęta")


class ProjectSearchForm(Form):
    name = StringField("Nazwa", filters=[strip_filter])
    street = StringField("Ulica", filters=[strip_filter])
    postcode = StringField("Kod pocztowy", filters=[strip_filter])
    city = StringField("Miasto", filters=[strip_filter])
    state = SelectField("Województwo", choices=STATES)
    country = SelectField("Kraj", choices=COUNTRIES)
    link = StringField("Link", filters=[strip_filter])
    color = SelectField("Kolor", choices=COLORS)
    deadline = DateField("Termin", validators=[Optional()])
    stage = SelectField("Etap", choices=STAGES)
    project_delivery_method = SelectField(
        "Sposób realizacji", choices=PROJECT_DELIVERY_METHODS
    )
    submit = SubmitField("Szukaj")
