import regex as re
from sqlalchemy import select
from wtforms import DateTimeLocalField, Form, HiddenField, SelectField, StringField
from wtforms.validators import InputRequired, Length, Optional, ValidationError
from wtforms.widgets import DateTimeLocalInput

from ..models import Tag
from .filters import strip_filter
from .select import CATEGORIES
from .ts import TranslationString as _


class TagForm(Form):
    name = StringField(
        _("Name"),
        validators=[
            InputRequired(),
            Length(min=3, max=50),
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
        # Accept any Unicode letter or digit as first character
        if not re.match(r"^[\p{L}\p{N}]", field.data or "", re.UNICODE):
            raise ValidationError(_("Name must start with a letter or digit."))
        if self.edited_item:
            if self.edited_item.name == field.data:
                return
        exists = self.request.dbsession.execute(
            select(Tag).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists:
            raise ValidationError(_("This name is already taken"))


class TagSearchForm(Form):
    name = StringField(_("Name"), filters=[strip_filter], render_kw={"autofocus": True})


class TagFilterForm(Form):
    name = HiddenField(_("Name"), filters=[strip_filter])
    category = SelectField(_("Category"), choices=CATEGORIES)
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


class TagLinkForm(Form):
    name = StringField(
        _("Name"),
        validators=[
            InputRequired(),
            Length(min=3, max=50),
        ],
        filters=[strip_filter],
        render_kw={"autofocus": True},
    )
