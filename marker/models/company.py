import datetime

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Sequence,
    Integer,
    Float,
    Unicode,
    DateTime,
    select,
    func,
)

from sqlalchemy.orm import (
    relationship,
    backref,
    object_session,
)

from slugify import slugify
from .meta import Base
from .user import recomended


companies_tags = Table(
    "companies_tags",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)

companies_persons = Table(
    "companies_persons",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "person_id",
        Integer,
        ForeignKey("persons.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)

companies_comments = Table(
    "companies_comments",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "comment_id",
        Integer,
        ForeignKey("comments.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, Sequence("companies_id_seq", 1, 1), primary_key=True)
    name = Column(Unicode(100))
    street = Column(Unicode(100))
    postcode = Column(Unicode(10))
    city = Column(Unicode(100))
    state = Column(Unicode(2))
    country = Column(Unicode(2))
    latitude = Column(Float)
    longitude = Column(Float)
    WWW = Column(Unicode(100))
    NIP = Column(Unicode(20))
    REGON = Column(Unicode(20))
    KRS = Column(Unicode(20))
    court = Column(Unicode(100))
    color = Column(Unicode(10))
    tags = relationship("Tag", secondary=companies_tags, backref="companies")
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
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    editor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
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
        WWW,
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
        self.WWW = WWW
        self.NIP = NIP
        self.REGON = REGON
        self.KRS = KRS
        self.court = court
        self.color = color

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def count_recomended(self):
        return object_session(self).scalar(
            select(func.count(recomended.c.company_id)).where(
                recomended.c.company_id == self.id
            )
        )
