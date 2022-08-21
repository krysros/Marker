from sqlalchemy import select
from wtforms import Form, StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from ..models import Tag
from .filters import strip_filter


class TagForm(Form):
    name = StringField(
        "Nazwa",
        validators=[
            InputRequired("Podaj tag"),
            Length(
                min=3,
                max=50,
                message="Długość musi zawierać się w przedziale %(min)d-%(max)d",
            ),
        ],
        filters=[strip_filter],
    )
    submit = SubmitField("Zapisz")

    def __init__(self, *args, dbsession, **kwargs):
        super().__init__(*args, **kwargs)
        self.dbsession = dbsession

    def validate_name(self, field):
        exists = self.dbsession.execute(
            select(Tag).filter_by(name=field.data)
        ).scalar_one_or_none()
        if exists:
            raise ValidationError("Ta nazwa jest już zajęta")


class TagSearchForm(Form):
    name = StringField("Nazwa", filters=[strip_filter])
    submit = SubmitField("Szukaj")
