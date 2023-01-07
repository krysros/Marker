import datetime

from sqlalchemy import (
    ForeignKey,
    Integer,
    Text,
    DateTime,
)

from sqlalchemy.orm import (
    mapped_column,
    relationship,
)
from .meta import Base


class Comment(Base):
    __tablename__ = "comments"
    id = mapped_column(Integer, primary_key=True)
    comment = mapped_column(Text())
    created_at = mapped_column(DateTime, default=datetime.datetime.now)
    updated_at = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    editor_id = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_by = relationship("User", foreign_keys=[creator_id])
    updated_by = relationship("User", foreign_keys=[editor_id])

    def __init__(self, comment):
        self.comment = comment
