from wtforms import EmailField, Form, HiddenField, StringField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length

from .filters import strip_filter
from .select import CONTACTS_FILTER
from .ts import TranslationString as _


class ContactForm(Form):
    name = StringField(
        _("Fullname"),
        validators=[
            InputRequired(),
            Length(min=5, max=100),
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
    submit = SubmitField(_("Save"))


class ContactSearchForm(Form):
    name = StringField(_("Fullname"), filters=[strip_filter])
    role = StringField(_("Role"), filters=[strip_filter])
    phone = StringField(_("Phone"), filters=[strip_filter])
    email = StringField(_("Email"), filters=[strip_filter])
    submit = SubmitField(_("Search"))


class ContactFilterForm(Form):
    name = HiddenField(_("Fullname"), filters=[strip_filter])
    role = HiddenField(_("Role"), filters=[strip_filter])
    phone = HiddenField(_("Phone"), filters=[strip_filter])
    email = HiddenField(_("Email"), filters=[strip_filter])
    filter = SelectField(_("Filter"), choices=CONTACTS_FILTER)
    submit = SubmitField(_("Search"))
