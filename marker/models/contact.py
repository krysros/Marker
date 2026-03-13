import datetime
from typing import TYPE_CHECKING, Optional

from slugify import slugify
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .meta import Base

if TYPE_CHECKING:
    from .company import Company
    from .project import Project
    from .user import User


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    role: Mapped[Optional[str]]
    phone: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    color: Mapped[Optional[str]]

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

    company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    company: Mapped["Company"] = relationship(back_populates="contacts")

    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    project: Mapped["Project"] = relationship(back_populates="contacts")

    def __init__(
        self,
        name: str | None,
        role: str | None,
        phone: str | None,
        email: str | None,
        color: str | None,
    ) -> None:
        self.name = name or ""
        self.role = role
        self.phone = phone
        self.email = email
        self.color = color

    @property
    def slug(self) -> str:
        return slugify(self.name or "")
