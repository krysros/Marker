import datetime

from slugify import slugify
from sqlalchemy import ForeignKey, Unicode, and_, func, select
from sqlalchemy.orm import Mapped, mapped_column, object_session, relationship

from .association import CompaniesProjects, projects_tags, watched
from .comment import Comment
from .meta import Base
from .person import Person
from .tag import Tag


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(200))
    street: Mapped[str] = mapped_column(Unicode(100))
    postcode: Mapped[str] = mapped_column(Unicode(10))
    city: Mapped[str] = mapped_column(Unicode(100))
    state: Mapped[str] = mapped_column(Unicode(2))
    country: Mapped[str] = mapped_column(Unicode(2))
    latitude: Mapped[float]
    longitude: Mapped[float]
    link: Mapped[str] = mapped_column(Unicode(2000))
    color: Mapped[str] = mapped_column(Unicode(10))
    deadline: Mapped[datetime.date]
    stage: Mapped[str] = mapped_column(Unicode(100))
    delivery_method: Mapped[str] = mapped_column(Unicode(100))

    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    editor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped["User"] = relationship(foreign_keys=[editor_id])

    tags: Mapped[list["Tag"]] = relationship(
        secondary=projects_tags, back_populates="projects"
    )
    companies: Mapped[list["CompaniesProjects"]] = relationship(
        back_populates="project"
    )
    people: Mapped[list["Person"]] = relationship(back_populates="project")
    comments: Mapped[list["Comment"]] = relationship(back_populates="project")

    def __init__(
        self,
        name: str,
        street: str,
        postcode: str,
        city: str,
        state: str,
        country: str,
        link: str,
        color: str,
        deadline: datetime.date,
        stage: str,
        delivery_method: str,
    ) -> None:
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
    def count_persons(self) -> int:
        return object_session(self).scalar(
            select(func.count()).select_from(Person).where(Person.project_id == self.id)
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
