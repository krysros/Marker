import datetime

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    Unicode,
    DateTime,
    Date,
)

from sqlalchemy.orm import relationship

from slugify import slugify
from .meta import Base


companies_investments = Table(
    "companies_investments",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "investment_id",
        Integer,
        ForeignKey("investments.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)


class Investment(Base):
    __tablename__ = "investments"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200))
    city = Column(Unicode(100))
    voivodeship = Column(Unicode(2))
    link = Column(Unicode(2000))
    deadline = Column(Date)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    editor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_by = relationship("User", foreign_keys=[creator_id])
    updated_by = relationship("User", foreign_keys=[editor_id])
    company = relationship(
        "Company",
        secondary=companies_investments,
        backref="investments",
        uselist=False,
    )

    def __init__(self, name, city, voivodeship, company, link, deadline):
        self.name = name
        self.city = city
        self.voivodeship = voivodeship
        self.company = company
        self.link = link
        self.deadline = deadline

    @property
    def slug(self):
        return slugify(self.name)
