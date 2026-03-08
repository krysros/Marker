from sqlalchemy import select
from wtforms import Form, HiddenField, SelectField, StringField
from wtforms.validators import InputRequired, Length, ValidationError

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
            select(Tag).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists:
            raise ValidationError(_("This name is already taken"))


class TagSearchForm(Form):
    name = StringField(_("Name"), filters=[strip_filter])


class TagFilterForm(Form):
    name = HiddenField(_("Name"), filters=[strip_filter])
    category = SelectField(_("Category"), choices=CATEGORIES)


class TagLinkForm(Form):
    name = StringField(
        _("Name"),
        validators=[
            InputRequired(),
            Length(min=3, max=50),
        ],
        filters=[strip_filter],
    )
