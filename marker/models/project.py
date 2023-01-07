import datetime

from sqlalchemy import (
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
    projects_tags,
    projects_persons,
    projects_comments,
    watched,
)


class Project(Base):
    __tablename__ = "projects"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(Unicode(200))
    street = mapped_column(Unicode(100))
    postcode = mapped_column(Unicode(10))
    city = mapped_column(Unicode(100))
    state = mapped_column(Unicode(2))
    country = mapped_column(Unicode(2))
    latitude = mapped_column(Float)
    longitude = mapped_column(Float)
    link = mapped_column(Unicode(2000))
    color = mapped_column(Unicode(10))
    deadline = mapped_column(Date)
    stage = mapped_column(Unicode(100))
    delivery_method = mapped_column(Unicode(100))
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
                    Tag.projects.any(Project.id == self.id),
                    Project.id != self.id,
                )
            )
        )
