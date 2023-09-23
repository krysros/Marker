from wtforms import EmailField, Form, HiddenField, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired, Length

from .filters import strip_filter, title
from .select import PARENTS
from .ts import TranslationString as _


class ContactForm(Form):
    name = StringField(
        _("Fullname"),
        validators=[
            InputRequired(),
            Length(min=5, max=100),
        ],
        filters=[strip_filter, title],
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


class ContactSearchForm(Form):
    name = StringField(_("Fullname"), filters=[strip_filter])
    role = StringField(_("Role"), filters=[strip_filter])
    phone = StringField(_("Phone"), filters=[strip_filter])
    email = StringField(_("Email"), filters=[strip_filter])


class ContactFilterForm(Form):
    name = HiddenField(_("Fullname"), filters=[strip_filter])
    role = HiddenField(_("Role"), filters=[strip_filter])
    phone = HiddenField(_("Phone"), filters=[strip_filter])
    email = HiddenField(_("Email"), filters=[strip_filter])
    parent = SelectField(_("Parent"), choices=PARENTS)
