from wtforms import Form, HiddenField, SelectField, TextAreaField
from wtforms.validators import InputRequired

from .filters import strip_filter
from .select import PARENTS
from .ts import TranslationString as _


class CommentForm(Form):
    comment = TextAreaField(
        _("Comment"),
        validators=[
            InputRequired(),
        ],
        filters=[strip_filter],
    )


class CommentSearchForm(Form):
    comment = TextAreaField(_("Comment"), filters=[strip_filter])


class CommentFilterForm(Form):
    comment = HiddenField(_("Comment"), filters=[strip_filter])
    parent = SelectField(_("Parent"), choices=PARENTS)
