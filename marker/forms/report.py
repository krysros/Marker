from wtforms import Form
from wtforms.fields import SelectField, SubmitField

from .select import REPORTS
from .ts import TranslationString as _


class ReportForm(Form):
    report = SelectField(_("Report"), choices=REPORTS)
    submit = SubmitField(_("Show"))
