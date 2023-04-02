import datetime
from typing import Optional

from slugify import slugify
from sqlalchemy import ForeignKey, Unicode
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .meta import Base


class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(100))
    role: Mapped[Optional[str]] = mapped_column(Unicode(100))
    phone: Mapped[Optional[str]] = mapped_column(Unicode(50))
    email: Mapped[Optional[str]] = mapped_column(Unicode(50))

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

    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="contacts")

    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="contacts")

    def __init__(
        self,
        name: str,
        role: str,
        phone: str,
        email: str,
    ) -> None:
        self.name = name
        self.role = role
        self.phone = phone
        self.email = email

    @property
    def slug(self) -> str:
        return slugify(self.name)
