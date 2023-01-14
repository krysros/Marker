import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from .meta import Base


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    editor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped["User"] = relationship(foreign_keys=[editor_id])

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="comments")

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="comments")

    def __init__(self, comment: str) -> None:
        self.comment = comment
