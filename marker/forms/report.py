from wtforms import Form
from wtforms.fields import SelectField, SubmitField
from marker.forms.select import REPORTS


class ReportForm(Form):
    report = SelectField("Raport", choices=REPORTS)
    submit = SubmitField("Pokaż")
