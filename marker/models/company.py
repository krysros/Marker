import datetime

from sqlalchemy import (
    ForeignKey,
    Sequence,
    Integer,
    Float,
    Unicode,
    DateTime,
    select,
    func,
    and_,
)

from sqlalchemy.orm import (
    mapped_column,
    relationship,
    object_session,
    backref,
)

from slugify import slugify

from .meta import Base
from .tag import Tag
from .tables import (
    companies_projects,
    companies_tags,
    companies_persons,
    companies_comments,
    recommended,
)


class Company(Base):
    __tablename__ = "companies"
    id = mapped_column(Integer, Sequence("companies_id_seq", 1, 1), primary_key=True)
    name = mapped_column(Unicode(100))
    street = mapped_column(Unicode(100))
    postcode = mapped_column(Unicode(10))
    city = mapped_column(Unicode(100))
    state = mapped_column(Unicode(2))
    country = mapped_column(Unicode(2))
    latitude = mapped_column(Float)
    longitude = mapped_column(Float)
    link = mapped_column(Unicode(100))
    NIP = mapped_column(Unicode(20))
    REGON = mapped_column(Unicode(20))
    KRS = mapped_column(Unicode(20))
    court = mapped_column(Unicode(100))
    color = mapped_column(Unicode(10))
    tags = relationship("Tag", secondary=companies_tags, backref="companies")
    projects = relationship(
        "Project", secondary=companies_projects, backref="companies"
    )
    people = relationship(
        "Person",
        secondary=companies_persons,
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="select",
        backref=backref("company", uselist=False),
    )
    comments = relationship(
        "Comment",
        secondary=companies_comments,
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="select",
        backref=backref("company", uselist=False),
    )
    created_at = mapped_column(DateTime, default=datetime.datetime.now)
    updated_at = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    editor_id = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_by = relationship("User", foreign_keys=[creator_id])
    updated_by = relationship("User", foreign_keys=[editor_id])

    def __init__(
        self,
        name,
        street,
        postcode,
        city,
        state,
        country,
        link,
        NIP,
        REGON,
        KRS,
        court,
        color,
    ):
        self.name = name
        self.street = street
        self.postcode = postcode
        self.city = city
        self.state = state
        self.country = country
        self.link = link
        self.NIP = NIP
        self.REGON = REGON
        self.KRS = KRS
        self.court = court
        self.color = color

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def count_projects(self):
        return object_session(self).scalar(
            select(func.count(companies_projects.c.company_id)).where(
                companies_projects.c.company_id == self.id
            )
        )

    @property
    def count_tags(self):
        return object_session(self).scalar(
            select(func.count(companies_tags.c.company_id)).where(
                companies_tags.c.company_id == self.id
            )
        )

    @property
    def count_persons(self):
        return object_session(self).scalar(
            select(func.count(companies_persons.c.company_id)).where(
                companies_persons.c.company_id == self.id
            )
        )

    @property
    def count_comments(self):
        return object_session(self).scalar(
            select(func.count(companies_comments.c.company_id)).where(
                companies_comments.c.company_id == self.id
            )
        )

    @property
    def count_recommended(self):
        return object_session(self).scalar(
            select(func.count(recommended.c.company_id)).where(
                recommended.c.company_id == self.id
            )
        )

    @property
    def count_similar(self):
        return object_session(self).scalar(
            select(func.count())
            .select_from(Company)
            .join(Tag, Company.tags)
            .filter(
                and_(
                    Tag.companies.any(Company.id == self.id),
                    Company.id != self.id,
                )
            )
        )
