from wtforms import Form, StringField
from wtforms.validators import URL, InputRequired, Length

from .filters import strip_filter
from .ts import TranslationString as _


class CompanyAddAIForm(Form):
    website = StringField(
        _("Company website address"),
        validators=[
            InputRequired(),
            Length(max=1000),
            URL(require_tld=True, message=_("Please enter a valid URL.")),
        ],
        filters=[strip_filter],
        render_kw={"placeholder": "https://example.com", "autofocus": True},
    )
