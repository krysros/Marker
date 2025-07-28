from wtforms import Form, SelectField

from .select import COMPANY_ROLES, STAGES
from .ts import TranslationString as _


class ActivityForm(Form):
    stage = SelectField(_("Stage"), choices=STAGES)
    role = SelectField(
        _("Role"),
        choices=COMPANY_ROLES,
    )
