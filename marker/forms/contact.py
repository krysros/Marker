import re

from wtforms import (
    EmailField,
    FileField,
    Form,
    HiddenField,
    SelectField,
    SelectMultipleField,
    StringField,
    ValidationError,
)
from wtforms.validators import DataRequired, InputRequired, Length

from .filters import remove_mailto, strip_filter
from .select import CATEGORIES, COLORS, select_countries, select_subdivisions
from .ts import TranslationString as _


class ContactForm(Form):
    name = StringField(
        _("Name"),
        validators=[
            InputRequired(),
            Length(max=100),
        ],
        filters=[strip_filter],
        render_kw={"autofocus": True},
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
        filters=[strip_filter, remove_mailto],
    )
    color = SelectField(_("Color"), choices=COLORS, default="")

    def validate_name(self, field):
        if not re.match(r"^[A-Za-z0-9]", field.data or ""):
            raise ValidationError(_("Name must start with a letter or digit."))


class ContactSearchForm(Form):
    name = StringField(_("Name"), filters=[strip_filter], render_kw={"autofocus": True})
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
    subdivision = SelectMultipleField(
        _("Subdivision"), choices=select_subdivisions(), validate_choice=False
    )
    country = SelectField(_("Country"), choices=select_countries())
    color = SelectField(_("Color"), choices=COLORS)

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


class ContactImportForm(Form):
    csv_file = FileField(_("CSV file"), validators=[DataRequired()])
