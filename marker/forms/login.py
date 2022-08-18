from wtforms import Form, StringField, PasswordField, SubmitField


class LoginForm(Form):
    username = StringField('Nazwa użytkownika')
    password = PasswordField('Hasło')
    submit = SubmitField('Zaloguj się')
