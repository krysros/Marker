from wtforms import Form, StringField
from wtforms.validators import URL, InputRequired, Length

from .ts import TranslationString as _


class ProjectAddAIForm(Form):
    website = StringField(
        _("Project website address"),
        validators=[
            InputRequired(),
            Length(max=100),
            URL(require_tld=True, message=_("Please enter a valid URL.")),
        ],
        render_kw={"placeholder": "https://example.com", "autofocus": True},
    )
