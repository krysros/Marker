import datetime

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Sequence,
    Integer,
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
from .user import upvotes


companies_branches = Table(
    "companies_branches",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "branch_id",
        Integer,
        ForeignKey("branches.id", onupdate="CASCADE", ondelete="CASCADE"),
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
    voivodeship = Column(Unicode(2))
    phone = Column(Unicode(50))
    email = Column(Unicode(100))
    www = Column(Unicode(100))
    nip = Column(Unicode(20))
    regon = Column(Unicode(20))
    krs = Column(Unicode(20))
    court = Column(Unicode(100))
    category = Column(Unicode(10))
    branches = relationship(
        "Branch", secondary=companies_branches, backref="companies"
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
        voivodeship,
        phone,
        email,
        www,
        nip,
        regon,
        krs,
        court,
        category,
        branches,
        people,
    ):
        self.name = name
        self.street = street
        self.postcode = postcode
        self.city = city
        self.voivodeship = voivodeship
        self.phone = phone
        self.email = email
        self.www = www
        self.nip = nip
        self.regon = regon
        self.krs = krs
        self.court = court
        self.category = category
        self.branches = branches
        self.people = people

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def upvote_count(self):
        return object_session(self).scalar(
            select([func.count(upvotes.c.company_id)]).where(
                upvotes.c.company_id == self.id
            )
        )
