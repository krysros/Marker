import re

from sqlalchemy import select
from wtforms import (
    DateTimeLocalField,
    DecimalField,
    Form,
    HiddenField,
    SelectField,
    SelectMultipleField,
    StringField,
)
from wtforms.validators import InputRequired, Length, Optional, ValidationError
from wtforms.widgets import DateTimeLocalInput

from ..models import Project
from .association import ActivityForm
from .filters import dash_filter, remove_multiple_spaces, strip_filter, title
from .select import (
    COLORS,
    OBJECT_CATEGORIES,
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
            Length(max=1000),
        ],
        filters=[strip_filter],
        render_kw={"autofocus": True},
    )
    street = StringField(
        _("Street"),
        validators=[Length(max=100)],
        filters=[strip_filter],
    )
    postcode = StringField(
        _("Post code"),
        validators=[Length(max=100)],
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
        validators=[Length(max=1000)],
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
    object_category = SelectField(
        _("Object category"),
        choices=OBJECT_CATEGORIES,
        validators=[Optional()],
    )
    delivery_method = SelectField(
        _("Project delivery method"), choices=PROJECT_DELIVERY_METHODS
    )
    usable_area = DecimalField(
        _("Usable area [m²]"),
        validators=[Optional()],
        places=2,
    )
    cubic_volume = DecimalField(
        _("Cubic volume [m³]"),
        validators=[Optional()],
        places=2,
    )

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None

        country = getattr(self.edited_item, "country", None)

        self.subdivision.choices = select_subdivisions(country)

    def validate_name(self, field):
        # Name must contain at least one letter or digit (Unicode)
        if not re.search(r"[\w\d]", field.data or "", re.UNICODE):
            raise ValidationError(_("Name must contain at least one letter or digit."))
        if self.edited_item:
            if self.edited_item.name == field.data:
                return
        exists = self.request.dbsession.execute(
            select(Project).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists:
            raise ValidationError(_("This name is already taken"))


class ProjectSearchForm(Form):
    name = StringField(_("Name"), filters=[strip_filter], render_kw={"autofocus": True})
    street = StringField(_("Street"), filters=[strip_filter])
    postcode = StringField(_("Post code"), filters=[strip_filter])
    city = StringField(_("City"), filters=[strip_filter])
    subdivision = SelectField(
        _("Subdivision"), choices=select_subdivisions(), validate_choice=False
    )
    country = SelectField(_("Country"), choices=select_countries())
    website = StringField(_("Website"), filters=[strip_filter])
    deadline_from = DateTimeLocalField(
        _("Deadline from"),
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
    deadline_to = DateTimeLocalField(
        _("Deadline to"),
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
    stage = SelectField(_("Stage"), choices=STAGES)
    delivery_method = SelectField(
        _("Project delivery method"), choices=PROJECT_DELIVERY_METHODS
    )
    usable_area_from = DecimalField(
        _("Usable area from [m²]"),
        validators=[Optional()],
        places=2,
    )
    usable_area_to = DecimalField(
        _("Usable area to [m²]"),
        validators=[Optional()],
        places=2,
    )
    cubic_volume_from = DecimalField(
        _("Cubic volume from [m³]"),
        validators=[Optional()],
        places=2,
    )
    cubic_volume_to = DecimalField(
        _("Cubic volume to [m³]"),
        validators=[Optional()],
        places=2,
    )
    color = SelectField(_("Color"), choices=COLORS)
    object_category = SelectField(
        _("Object category"),
        choices=OBJECT_CATEGORIES,
        validators=[Optional()],
    )


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
    deadline_from = DateTimeLocalField(
        _("Deadline from"),
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
    deadline_to = DateTimeLocalField(
        _("Deadline to"),
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
    stage = SelectField(_("Stage"), choices=STAGES)
    delivery_method = SelectField(
        _("Project delivery method"), choices=PROJECT_DELIVERY_METHODS
    )
    status = SelectField(_("Status"), choices=STATUS)
    color = SelectField(_("Color"), choices=COLORS)
    usable_area_from = DecimalField(
        _("Usable area from [m²]"),
        validators=[Optional()],
        places=2,
    )
    usable_area_to = DecimalField(
        _("Usable area to [m²]"),
        validators=[Optional()],
        places=2,
    )
    cubic_volume_from = DecimalField(
        _("Cubic volume from [m³]"),
        validators=[Optional()],
        places=2,
    )
    cubic_volume_to = DecimalField(
        _("Cubic volume to [m³]"),
        validators=[Optional()],
        places=2,
    )
    date_from = DateTimeLocalField(
        _("Date from"),
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
    date_to = DateTimeLocalField(
        _("Date to"),
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
    object_category = SelectField(
        _("Object category"),
        choices=OBJECT_CATEGORIES,
        validators=[Optional()],
    )

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None

        country = getattr(self.edited_item, "country", None)

        self.subdivision.choices = select_subdivisions(country)
        self.subdivision.default = self.request.GET.getall("subdivision")


class ProjectActivityForm(ActivityForm):
    name = StringField(
        _("Name"), validators=[InputRequired()], render_kw={"autofocus": True}
    )

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None

    def validate_name(self, field):
        if self.edited_item:
            if self.edited_item.name == field.data:
                return
        exists = self.request.dbsession.execute(
            select(Project).filter_by(name=field.data)
        ).scalar_one_or_none()
        if not exists:
            raise ValidationError(_("There is no project with this name"))


class ProjectLinkForm(Form):
    name = StringField(
        _("Name"),
        validators=[
            InputRequired(),
            Length(max=1000),
        ],
        filters=[strip_filter],
        render_kw={"autofocus": True},
    )

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        try:
            self.edited_item = args[1]
        except IndexError:
            self.edited_item = None

    def validate_name(self, field):
        if self.edited_item and self.edited_item.name == field.data:
            return
        exists = self.request.dbsession.execute(
            select(Project).filter_by(name=field.data)
        ).scalar_one_or_none()
        if not exists:
            raise ValidationError(_("There is no project with this name"))
