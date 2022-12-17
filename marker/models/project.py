import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Float,
    Unicode,
    DateTime,
    Date,
    select,
    func,
    and_,
)

from sqlalchemy.orm import (
    relationship,
    object_session,
    backref,
)

from slugify import slugify
from .meta import Base
from .tag import Tag
from .tables import (
    companies_projects,
    projects_tags,
    projects_persons,
    projects_comments,
    watched,
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
    color = Column(Unicode(10))
    deadline = Column(Date)
    stage = Column(Unicode(100))
    delivery_method = Column(Unicode(100))
    tags = relationship("Tag", secondary=projects_tags, backref="projects")
    people = relationship(
        "Person",
        secondary=projects_persons,
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="select",
        backref=backref("project", uselist=False),
    )
    comments = relationship(
        "Comment",
        secondary=projects_comments,
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="select",
        backref=backref("project", uselist=False),
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
        link,
        color,
        deadline,
        stage,
        delivery_method,
    ):
        self.name = name
        self.street = street
        self.postcode = postcode
        self.city = city
        self.state = state
        self.country = country
        self.link = link
        self.color = color
        self.deadline = deadline
        self.stage = stage
        self.delivery_method = delivery_method

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def count_companies(self):
        return object_session(self).scalar(
            select(func.count(companies_projects.c.project_id)).where(
                companies_projects.c.project_id == self.id
            )
        )

    @property
    def count_tags(self):
        return object_session(self).scalar(
            select(func.count(projects_tags.c.project_id)).where(
                projects_tags.c.project_id == self.id
            )
        )

    @property
    def count_persons(self):
        return object_session(self).scalar(
            select(func.count(projects_persons.c.project_id)).where(
                projects_persons.c.project_id == self.id
            )
        )

    @property
    def count_comments(self):
        return object_session(self).scalar(
            select(func.count(projects_comments.c.project_id)).where(
                projects_comments.c.project_id == self.id
            )
        )

    @property
    def count_watched(self):
        return object_session(self).scalar(
            select(func.count(watched.c.project_id)).where(
                watched.c.project_id == self.id
            )
        )

    @property
    def count_similar(self):
        return object_session(self).scalar(
            select(func.count())
            .select_from(Project)
            .join(Tag, Project.tags)
            .filter(
                and_(
                    Tag.companies.any(Project.id == self.id),
                    Project.id != self.id,
                )
            )
        )
