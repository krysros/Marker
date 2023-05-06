from wtforms import Form, PasswordField, StringField, SubmitField

from .ts import TranslationString as _


class LoginForm(Form):
    username = StringField(_("User name"))
    password = PasswordField(_("Password"))
