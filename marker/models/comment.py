import datetime
from datetime import UTC
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .meta import Base

if TYPE_CHECKING:
    from .company import Company
    from .project import Project
    from .user import User


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str]

    created_at: Mapped[datetime.datetime] = mapped_column(
        default=lambda: datetime.datetime.now(UTC)
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        default=lambda: datetime.datetime.now(UTC),
        onupdate=lambda: datetime.datetime.now(UTC),
    )

    creator_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    editor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped[Optional["User"]] = relationship(foreign_keys=[editor_id])

    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="comments")

    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="comments")

    def __init__(self, comment: str) -> None:
        self.comment = comment
