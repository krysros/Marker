from wtforms import Form, PasswordField, StringField, SubmitField


class LoginForm(Form):
    username = StringField("Nazwa użytkownika")
    password = PasswordField("Hasło")
    submit = SubmitField("Zaloguj się")
