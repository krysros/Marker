from sqlalchemy import select
from wtforms import (
    DateTimeLocalField,
    Form,
    HiddenField,
    SelectField,
    SelectMultipleField,
    StringField,
)
from wtforms.validators import InputRequired, Length, Optional, ValidationError
from wtforms.widgets import DateTimeLocalInput

from ..models import Project
from .filters import dash_filter, remove_multiple_spaces, strip_filter, title
from .select import (
    COLORS,
    PROJECT_DELIVERY_METHODS,
    STAGES,
    STATUS,
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
        filters=[strip_filter, title],
    )
    subdivision = SelectField(
        _("Subdivision"), choices=select_subdivisions(), validate_choice=False
    )
    country = SelectField(_("Country"), choices=select_countries())
    website = StringField(
        _("Website"),
        validators=[Length(max=2000)],
        filters=[strip_filter],
    )
    color = SelectField(_("Color"), choices=COLORS, default="")
    deadline = DateTimeLocalField(
        _("Deadline"),
        format="%Y-%m-%dT%H:%M",  # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/datetime-local
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
    stage = SelectField(_("Stage"), choices=STAGES)
    delivery_method = SelectField(
        _("Project delivery method"), choices=PROJECT_DELIVERY_METHODS
    )

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
    website = StringField(_("Website"), filters=[strip_filter])
    deadline = DateTimeLocalField(
        _("Deadline"),
        format="%Y-%m-%dT%H:%M",  # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/datetime-local
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
    stage = SelectField(_("Stage"), choices=STAGES)
    delivery_method = SelectField(
        _("Project delivery method"), choices=PROJECT_DELIVERY_METHODS
    )
    color = SelectField(_("Color"), choices=COLORS)


class ProjectFilterForm(Form):
    name = HiddenField(_("Name"), filters=[strip_filter])
    street = HiddenField(_("Street"), filters=[strip_filter])
    postcode = HiddenField(_("Post code"), filters=[strip_filter])
    city = HiddenField(_("City"), filters=[strip_filter])
    subdivision = SelectMultipleField(
        _("Subdivision"), choices=select_subdivisions(), validate_choice=False
    )
    country = SelectField(_("Country"), choices=select_countries())
    website = HiddenField(_("Website"), filters=[strip_filter])
    deadline = HiddenField(_("Deadline"))
    stage = SelectField(_("Stage"), choices=STAGES)
    delivery_method = SelectField(
        _("Project delivery method"), choices=PROJECT_DELIVERY_METHODS
    )
    status = SelectField(_("Status"), choices=STATUS)
    color = SelectField(_("Color"), choices=COLORS)

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
        self.subdivision.default = self.request.GET.getall("subdivision")
