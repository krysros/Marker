from wtforms import DecimalField, Form, SelectField
from wtforms.validators import Optional

from .select import COMPANY_ROLES, STAGES, select_currencies
from .ts import TranslationString as _


class ActivityForm(Form):
    stage = SelectField(_("Stage"), choices=STAGES)
    role = SelectField(
        _("Role"),
        choices=COMPANY_ROLES,
    )
    currency = SelectField(_("Currency"), choices=select_currencies())
    value_net = DecimalField(
        _("Net value"),
        validators=[Optional()],
        places=2,
    )
    value_gross = DecimalField(
        _("Gross value"),
        validators=[Optional()],
        places=2,
    )
