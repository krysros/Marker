import datetime

from sqlalchemy import (
    Unicode,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from slugify import slugify
from .meta import Base


class Person(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(100))
    position: Mapped[str] = mapped_column(Unicode(100))
    phone: Mapped[str] = mapped_column(Unicode(50))
    email: Mapped[str] = mapped_column(Unicode(50))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    editor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped["User"] = relationship(foreign_keys=[editor_id])

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="people")

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="people")


    def __init__(
        self,
        name: str,
        position: str,
        phone: str,
        email: str,
    ) -> None:
        self.name = name
        self.position = position
        self.phone = phone
        self.email = email

    @property
    def slug(self) -> str:
        return slugify(self.name)
