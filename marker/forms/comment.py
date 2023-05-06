from wtforms import Form, HiddenField, SelectField, SubmitField, TextAreaField

from .filters import strip_filter
from .select import TYP_FILTER
from .ts import TranslationString as _


class CommentForm(Form):
    comment = TextAreaField(_("Comment"), filters=[strip_filter])


class CommentSearchForm(Form):
    comment = TextAreaField(_("Comment"), filters=[strip_filter])


class CommentFilterForm(Form):
    comment = HiddenField(_("Comment"), filters=[strip_filter])
    typ = SelectField(_("Type"), choices=TYP_FILTER)
