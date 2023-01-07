import datetime

from sqlalchemy import (
    Integer,
    Unicode,
    DateTime,
    ForeignKey,
    select,
    func,
)

from sqlalchemy.orm import (
    mapped_column,
    relationship,
    object_session,
)

from slugify import slugify
from .meta import Base
from .tables import (
    companies_tags,
    projects_tags,
)


class Tag(Base):
    __tablename__ = "tags"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(Unicode(50))
    created_at = mapped_column(DateTime, default=datetime.datetime.now)
    updated_at = mapped_column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    editor_id = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_by = relationship("User", foreign_keys=[creator_id])
    updated_by = relationship("User", foreign_keys=[editor_id])

    def __init__(self, name):
        self.name = name

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def count_companies(self):
        return object_session(self).scalar(
            select(func.count(companies_tags.c.tag_id)).where(
                companies_tags.c.tag_id == self.id
            )
        )

    @property
    def count_projects(self):
        return object_session(self).scalar(
            select(func.count(projects_tags.c.tag_id)).where(
                projects_tags.c.tag_id == self.id
            )
        )
