from sqlalchemy import select
from wtforms import DateField, Form, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired, Length, Optional, ValidationError

from ..models import Project
from .filters import dash_filter, remove_multiple_spaces, strip_filter
from .select import (
    COLORS,
    PROJECT_DELIVERY_METHODS,
    STAGES,
    select_countries,
    select_subdivisions,
)
from .ts import TranslationString as _


class ProjectForm(Form):
    name = StringField(
        _("Name"),
        validators=[
            InputRequired(),
            Length(max=200),
        ],
        filters=[strip_filter],
    )
    street = StringField(
        _("Street"),
        validators=[Length(max=100)],
        filters=[strip_filter],
    )
    postcode = StringField(
        _("Post code"),
        validators=[Length(max=10)],
        filters=[strip_filter, dash_filter, remove_multiple_spaces],
    )
    city = StringField(
        _("City"),
        validators=[Length(max=100)],
        filters=[strip_filter],
    )
    subdivision = SelectField(_("Subdivision"), choices=select_subdivisions(), validate_choice=False)
    country = SelectField(_("Country"), choices=select_countries())
    link = StringField(
        _("Link"),
        validators=[Length(max=2000)],
        filters=[strip_filter],
    )
    color = SelectField(_("Color"), choices=COLORS, default="default")
    deadline = DateField(_("Deadline"), validators=[Optional()])
    stage = SelectField(_("Stage"), choices=STAGES)
    delivery_method = SelectField(
        _("Project delivery method"), choices=PROJECT_DELIVERY_METHODS
    )
    submit = SubmitField(_("Save"))

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None

        try:
            country = self.edited_item.country
        except AttributeError:
            country = None

        self.subdivision.choices = select_subdivisions(country)

    def validate_name(self, field):
        if self.edited_item:
            if self.edited_item.name == field.data:
                return
        exists = self.request.dbsession.execute(
            select(Project).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists:
            raise ValidationError(_("This name is already taken"))


class ProjectSearchForm(Form):
    name = StringField(_("Name"), filters=[strip_filter])
    street = StringField(_("Street"), filters=[strip_filter])
    postcode = StringField(_("Post code"), filters=[strip_filter])
    city = StringField(_("City"), filters=[strip_filter])
    subdivision = SelectField(_("Subdivision"), choices=select_subdivisions())
    country = SelectField(_("Country"), choices=select_countries())
    link = StringField(_("Link"), filters=[strip_filter])
    deadline = DateField(_("Deadline"), validators=[Optional()])
    stage = SelectField(_("Stage"), choices=STAGES)
    delivery_method = SelectField(
        _("Project delivery method"), choices=PROJECT_DELIVERY_METHODS
    )
    color = SelectField(_("Color"), choices=COLORS)
    submit = SubmitField(_("Search"))
