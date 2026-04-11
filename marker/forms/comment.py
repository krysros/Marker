from wtforms import DateTimeLocalField, Form, HiddenField, SelectField, TextAreaField
from wtforms.validators import InputRequired, Optional
from wtforms.widgets import DateTimeLocalInput

from .filters import strip_filter
from .select import CATEGORIES
from .ts import TranslationString as _


class CommentForm(Form):
    comment = TextAreaField(
        _("Comment"),
        validators=[
            InputRequired(),
        ],
        filters=[strip_filter],
        render_kw={"autofocus": True},
    )


class CommentSearchForm(Form):
    comment = TextAreaField(
        _("Comment"), filters=[strip_filter], render_kw={"autofocus": True}
    )


class CommentFilterForm(Form):
    comment = HiddenField(_("Comment"), filters=[strip_filter])
    category = SelectField(_("Category"), choices=CATEGORIES)
    date_from = DateTimeLocalField(
        _("Date from"),
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
    date_to = DateTimeLocalField(
        _("Date to"),
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        widget=DateTimeLocalInput(),
    )
