import datetime
from typing import Optional

from slugify import slugify
from sqlalchemy import ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, object_session, relationship

from .association import companies_tags, projects_tags
from .meta import Base


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    creator_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    editor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped[Optional["User"]] = relationship(foreign_keys=[editor_id])

    companies: Mapped[list["Company"]] = relationship(
        secondary=companies_tags, back_populates="tags"
    )
    projects: Mapped[list["Project"]] = relationship(
        secondary=projects_tags, back_populates="tags"
    )

    def __init__(self, name: str) -> None:
        self.name = name

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def count_companies(self) -> int:
        return object_session(self).scalar(
            select(func.count(companies_tags.c.tag_id)).where(
                companies_tags.c.tag_id == self.id
            )
        )

    @property
    def count_projects(self) -> int:
        return object_session(self).scalar(
            select(func.count(projects_tags.c.tag_id)).where(
                projects_tags.c.tag_id == self.id
            )
        )
