from sqlalchemy import select
from wtforms import (
    EmailField,
    Form,
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
)
from wtforms.validators import InputRequired, Length, ValidationError
from zxcvbn import zxcvbn

from ..models import User
from .filters import strip_filter
from .select import USER_ROLES
from .ts import TranslationString as _


class UserForm(Form):
    name = StringField(
        _("Name"),
        validators=[
            InputRequired(),
            Length(min=3, max=30),
        ],
        filters=[strip_filter],
    )
    fullname = StringField(
        _("Fullname"),
        validators=[
            InputRequired(),
            Length(min=3, max=50),
        ],
        filters=[strip_filter],
    )
    email = EmailField(_("Email"), validators=[InputRequired()], filters=[strip_filter])
    role = SelectField(_("Role"), validators=[InputRequired()], choices=USER_ROLES)
    password = PasswordField(
        _("Password"),
        validators=[
            InputRequired(),
            Length(min=5),
        ],
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
            select(User).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists and self.request.identity.name != exists.name:
            raise ValidationError(_("This name is already taken"))

    def validate_password(form, field):
        results = zxcvbn(field.data)
        if results["score"] < 3:
            raise ValidationError(_("The password is too simple"))


class UserSearchForm(Form):
    name = StringField(_("Name"), filters=[strip_filter])
    fullname = StringField(_("Fullname"), filters=[strip_filter])
    email = StringField(_("Email"), filters=[strip_filter])
    role = SelectField(_("Role"), choices=USER_ROLES)


class UserFilterForm(Form):
    name = HiddenField(_("Name"), filters=[strip_filter])
    fullname = HiddenField(_("Fullname"), filters=[strip_filter])
    email = HiddenField(_("Email"), filters=[strip_filter])
    role = SelectField(_("Role"), choices=USER_ROLES)
