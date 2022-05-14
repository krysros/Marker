import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Unicode,
    DateTime,
)

from sqlalchemy.orm import relationship

from slugify import slugify
from .meta import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(Unicode(200))
    typ = Column(Unicode(50))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    editor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_by = relationship("User", foreign_keys=[creator_id])
    updated_by = relationship("User", foreign_keys=[editor_id])

    def __init__(self, filename, typ):
        self.filename = filename
        self.typ = typ

    @property
    def slug(self):
        return slugify(self.filename)
