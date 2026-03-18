from wtforms import Form, SelectMultipleField

from .select import COMPANY_ROLES
from .ts import TranslationString as _


class ContractorFilterForm(Form):
    role = SelectMultipleField(
        _("Role"),
        choices=[(value, label) for value, label in COMPANY_ROLES if value],
    )

    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.role.default = self.request.GET.getall("role")
