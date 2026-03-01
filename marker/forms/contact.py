from wtforms import EmailField, FileField, Form, HiddenField, SelectField, StringField
from wtforms.validators import DataRequired, InputRequired, Length

from .filters import strip_filter
from .select import CATEGORIES, COLORS
from .ts import TranslationString as _


class ContactForm(Form):
    name = StringField(
        _("Name"),
        validators=[
            InputRequired(),
            Length(max=100),
        ],
        filters=[strip_filter],
    )
    role = StringField(
        _("Role"),
        validators=[
            Length(max=100),
        ],
        filters=[strip_filter],
    )
    phone = StringField(
        _("Phone"),
        validators=[
            Length(max=50),
        ],
        filters=[strip_filter],
    )
    email = EmailField(
        _("Email"),
        validators=[
            Length(max=50),
        ],
        filters=[strip_filter],
    )
    color = SelectField(_("Color"), choices=COLORS, default="")


class ContactSearchForm(Form):
    name = StringField(_("Name"), filters=[strip_filter])
    role = StringField(_("Role"), filters=[strip_filter])
    phone = StringField(_("Phone"), filters=[strip_filter])
    email = StringField(_("Email"), filters=[strip_filter])
    color = SelectField(_("Color"), choices=COLORS)


class ContactFilterForm(Form):
    name = HiddenField(_("Name"), filters=[strip_filter])
    role = HiddenField(_("Role"), filters=[strip_filter])
    phone = HiddenField(_("Phone"), filters=[strip_filter])
    email = HiddenField(_("Email"), filters=[strip_filter])
    category = SelectField(_("Category"), choices=CATEGORIES)
    color = SelectField(_("Color"), choices=COLORS)


class ContactImportForm(Form):
    csv_file = FileField(_("CSV file"), validators=[DataRequired()])
