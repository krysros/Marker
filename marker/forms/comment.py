from wtforms import Form, SubmitField, TextAreaField

from .filters import strip_filter
from .ts import TranslationString as _


class CommentForm(Form):
    comment = TextAreaField(_("Comment"), filters=[strip_filter])
    submit = SubmitField(_("Save"))


class CommentSearchForm(Form):
    comment = TextAreaField(_("Comment"), filters=[strip_filter])
    submit = SubmitField(_("Search"))
