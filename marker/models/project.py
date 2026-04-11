import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from slugify import slugify
from sqlalchemy import ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, object_session, relationship

from .association import Activity, projects_stars, projects_tags
from .comment import Comment
from .contact import Contact
from .meta import Base
from .tag import Tag

if TYPE_CHECKING:
    from .user import User


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
    website: Mapped[Optional[str]]
    color: Mapped[Optional[str]]
    deadline: Mapped[Optional[datetime.datetime]]
    stage: Mapped[Optional[str]]
    delivery_method: Mapped[Optional[str]]
    usable_area: Mapped[Optional[Decimal]]
    cubic_volume: Mapped[Optional[Decimal]]
    currency: Mapped[Optional[str]]
    value_net: Mapped[Optional[Decimal]]
    value_gross: Mapped[Optional[Decimal]]

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
        name: str | None,
        street: str | None,
        postcode: str | None,
        city: str | None,
        subdivision: str | None,
        country: str | None,
        website: str | None,
        color: str | None,
        deadline: datetime.datetime | None,
        stage: str | None,
        delivery_method: str | None,
        usable_area: Decimal | None = None,
        cubic_volume: Decimal | None = None,
        currency: str | None = None,
        value_net: Decimal | None = None,
        value_gross: Decimal | None = None,
    ) -> None:
        self.name = name or ""
        self.street = street
        self.postcode = postcode
        self.city = city
        self.subdivision = subdivision
        self.country = country
        self.website = website
        self.color = color
        self.deadline = deadline
        self.stage = stage
        self.delivery_method = delivery_method
        self.usable_area = usable_area
        self.cubic_volume = cubic_volume
        self.currency = currency
        self.value_net = value_net
        self.value_gross = value_gross

    @property
    def slug(self) -> str:
        return slugify(self.name or "")

    def _scalar_count(self, stmt) -> int:
        session = object_session(self)
        if session is None:
            return 0
        value = session.scalar(stmt)
        return int(value or 0)

    @property
    def count_companies(self) -> int:
        return self._scalar_count(
            select(func.count()).where(Activity.project_id == self.id)
        )

    @property
    def count_tags(self) -> int:
        return self._scalar_count(
            select(func.count()).where(projects_tags.c.project_id == self.id)
        )

    @property
    def count_contacts(self) -> int:
        return self._scalar_count(
            select(func.count())
            .select_from(Contact)
            .where(Contact.project_id == self.id)
        )

    @property
    def count_comments(self) -> int:
        return self._scalar_count(
            select(func.count())
            .select_from(Comment)
            .where(Comment.project_id == self.id)
        )

    @property
    def count_stars(self) -> int:
        return self._scalar_count(
            select(func.count()).where(projects_stars.c.project_id == self.id)
        )

    @property
    def count_similar(self) -> int:
        base_tags = projects_tags.alias("base_tags")
        other_tags = projects_tags.alias("other_tags")
        return self._scalar_count(
            select(func.count(func.distinct(other_tags.c.project_id)))
            .select_from(
                base_tags.join(other_tags, base_tags.c.tag_id == other_tags.c.tag_id)
            )
            .where(
                base_tags.c.project_id == self.id,
                other_tags.c.project_id != self.id,
            )
        )
