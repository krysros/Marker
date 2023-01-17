from wtforms import Form, SubmitField, TextAreaField

from .filters import strip_filter


class CommentForm(Form):
    comment = TextAreaField("Komentarz", filters=[strip_filter])
    submit = SubmitField("Zapisz")


class CommentSearchForm(Form):
    comment = TextAreaField("Komentarz", filters=[strip_filter])
    submit = SubmitField("Szukaj")
