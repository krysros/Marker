import datetime

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    Float,
    Unicode,
    DateTime,
    Date,
    select,
    func,
)

from sqlalchemy.orm import (
    relationship,
    object_session,
)

from slugify import slugify
from .meta import Base
from .user import watched


companies_projects = Table(
    "companies_projects",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "project_id",
        Integer,
        ForeignKey("projects.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200))
    street = Column(Unicode(100))
    postcode = Column(Unicode(10))
    city = Column(Unicode(100))
    state = Column(Unicode(2))
    country = Column(Unicode(2))
    latitude = Column(Float)
    longitude = Column(Float)
    link = Column(Unicode(2000))
    deadline = Column(Date)
    stage = Column(Unicode(100))
    project_delivery_method = Column(Unicode(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    editor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_by = relationship("User", foreign_keys=[creator_id])
    updated_by = relationship("User", foreign_keys=[editor_id])
    companies = relationship(
        "Company",
        secondary=companies_projects,
        backref="projects",
    )

    def __init__(
        self,
        name,
        street,
        postcode,
        city,
        state,
        country,
        link,
        deadline,
        stage,
        project_delivery_method,
    ):
        self.name = name
        self.street = street
        self.postcode = postcode
        self.city = city
        self.state = state
        self.country = country
        self.link = link
        self.deadline = deadline
        self.stage = stage
        self.project_delivery_method = project_delivery_method

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def count_watched(self):
        return object_session(self).scalar(
            select(func.count(watched.c.project_id)).where(
                watched.c.project_id == self.id
            )
        )
