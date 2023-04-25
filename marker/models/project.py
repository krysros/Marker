import datetime
from typing import Optional

from slugify import slugify
from sqlalchemy import ForeignKey, Unicode, and_, func, select
from sqlalchemy.orm import Mapped, mapped_column, object_session, relationship

from .association import CompaniesProjects, projects_tags, watched
from .comment import Comment
from .contact import Contact
from .meta import Base
from .tag import Tag


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(200))
    street: Mapped[Optional[str]] = mapped_column(Unicode(100))
    postcode: Mapped[Optional[str]] = mapped_column(Unicode(10))
    city: Mapped[Optional[str]] = mapped_column(Unicode(100))
    subdivision: Mapped[Optional[str]] = mapped_column(Unicode(10))
    country: Mapped[Optional[str]] = mapped_column(Unicode(2))
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]
    link: Mapped[Optional[str]] = mapped_column(Unicode(2000))
    color: Mapped[Optional[str]] = mapped_column(Unicode(10))
    deadline: Mapped[Optional[datetime.datetime]]
    stage: Mapped[Optional[str]] = mapped_column(Unicode(100))
    delivery_method: Mapped[Optional[str]] = mapped_column(Unicode(100))

    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    editor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped[Optional["User"]] = relationship(foreign_keys=[editor_id])

    tags: Mapped[list["Tag"]] = relationship(
        secondary=projects_tags, back_populates="projects"
    )
    companies: Mapped[list["CompaniesProjects"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    def __init__(
        self,
        name: str,
        street: str,
        postcode: str,
        city: str,
        subdivision: str,
        country: str,
        link: str,
        color: str,
        deadline: datetime.datetime,
        stage: str,
        delivery_method: str,
    ) -> None:
        self.name = name
        self.street = street
        self.postcode = postcode
        self.city = city
        self.subdivision = subdivision
        self.country = country
        self.link = link
        self.color = color
        self.deadline = deadline
        self.stage = stage
        self.delivery_method = delivery_method

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def count_companies(self) -> int:
        return object_session(self).scalar(
            select(func.count(CompaniesProjects.project_id)).where(
                CompaniesProjects.project_id == self.id
            )
        )

    @property
    def count_tags(self) -> int:
        return object_session(self).scalar(
            select(func.count(projects_tags.c.project_id)).where(
                projects_tags.c.project_id == self.id
            )
        )

    @property
    def count_contacts(self) -> int:
        return object_session(self).scalar(
            select(func.count())
            .select_from(Contact)
            .where(Contact.project_id == self.id)
        )

    @property
    def count_comments(self) -> int:
        return object_session(self).scalar(
            select(func.count())
            .select_from(Comment)
            .where(Comment.project_id == self.id)
        )

    @property
    def count_watched(self) -> int:
        return object_session(self).scalar(
            select(func.count(watched.c.project_id)).where(
                watched.c.project_id == self.id
            )
        )

    @property
    def count_similar(self) -> int:
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
