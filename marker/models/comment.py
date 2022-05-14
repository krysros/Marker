import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    DateTime,
)

from sqlalchemy.orm import relationship
from .meta import Base


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    comment = Column(Text())
    created_at = Column(DateTime, default=datetime.datetime.now)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_by = relationship("User", foreign_keys=[creator_id])

    def __init__(self, comment):
        self.comment = comment
