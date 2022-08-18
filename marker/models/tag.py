import datetime

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from slugify import slugify
from .meta import Base


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    editor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_by = relationship("User", foreign_keys=[creator_id])
    updated_by = relationship("User", foreign_keys=[editor_id])

    def __init__(self, name):
        self.name = name

    @property
    def slug(self):
        return slugify(self.name)
