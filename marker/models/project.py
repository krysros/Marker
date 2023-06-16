import datetime
from typing import Optional

from slugify import slugify
from sqlalchemy import ForeignKey, and_, func, select
from sqlalchemy.orm import Mapped, mapped_column, object_session, relationship

from .association import Activity, projects_stars, projects_tags
from .comment import Comment
from .contact import Contact
from .meta import Base
from .tag import Tag


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    street: Mapped[Optional[str]]
    postcode: Mapped[Optional[str]]
    city: Mapped[Optional[str]]
    subdivision: Mapped[Optional[str]]
    country: Mapped[Optional[str]]
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]
    link: Mapped[Optional[str]]
    color: Mapped[Optional[str]]
    deadline: Mapped[Optional[datetime.datetime]]
    stage: Mapped[Optional[str]]
    delivery_method: Mapped[Optional[str]]

    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    creator_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    editor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped[Optional["User"]] = relationship(foreign_keys=[editor_id])

    tags: Mapped[list["Tag"]] = relationship(
        secondary=projects_tags, back_populates="projects"
    )
    companies: Mapped[list["Activity"]] = relationship(
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
            select(func.count(Activity.project_id)).where(
                Activity.project_id == self.id
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
    def count_stars(self) -> int:
        return object_session(self).scalar(
            select(func.count(projects_stars.c.project_id)).where(
                projects_stars.c.project_id == self.id
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
