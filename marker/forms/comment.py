from wtforms import Form, SubmitField, SelectField, TextAreaField

from .filters import strip_filter
from .select import COMMENTS_FILTER
from .ts import TranslationString as _


class CommentForm(Form):
    comment = TextAreaField(_("Comment"), filters=[strip_filter])
    submit = SubmitField(_("Save"))


class CommentSearchForm(Form):
    comment = TextAreaField(_("Comment"), filters=[strip_filter])
    submit = SubmitField(_("Search"))


class CommentFilterForm(Form):
    filter = SelectField(_("Filter"), choices=COMMENTS_FILTER)
    submit = SubmitField(_("Search"))
