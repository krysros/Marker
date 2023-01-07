import datetime
from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import (
    mapped_column,
    relationship,
)

from slugify import slugify
from .meta import Base


class Person(Base):
    __tablename__ = "persons"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(Unicode(100))
    position = mapped_column(Unicode(100))
    phone = mapped_column(Unicode(50))
    email = mapped_column(Unicode(50))
    created_at = mapped_column(DateTime, default=datetime.datetime.now)
    updated_at = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    editor_id = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_by = relationship("User", foreign_keys=[creator_id])
    updated_by = relationship("User", foreign_keys=[editor_id])

    def __init__(
        self,
        name,
        position,
        phone,
        email,
    ):
        self.name = name
        self.position = position
        self.phone = phone
        self.email = email

    @property
    def slug(self):
        return slugify(self.name)
