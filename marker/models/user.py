import datetime

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    Unicode,
    DateTime,
)

from sqlalchemy.orm import relationship

from .meta import Base
import argon2

ph = argon2.PasswordHasher()


recommended = Table(
    "recommended",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)


watched = Table(
    "watched",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("projects.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)


checked = Table(
    "checked",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(30), unique=True)
    fullname = Column(Unicode(50))
    email = Column(Unicode(50))
    role = Column(Unicode(20))
    _password = Column("password", Unicode(255))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pw):
        self._password = ph.hash(pw)

    def check_password(self, pw):
        try:
            ph.verify(self.password, pw)
            if ph.check_needs_rehash(self.password):
                self.password = pw
            return True
        except argon2.exceptions.VerifyMismatchError as error:
            return False

    recommended = relationship(
        "Company",
        secondary=recommended,
        cascade="delete",
        single_parent=True,
        backref="companies",
    )

    watched = relationship(
        "Project",
        secondary=watched,
        cascade="delete",
        single_parent=True,
        backref="projects",
    )

    checked = relationship(
        "Company",
        secondary=checked,
        cascade="delete",
        single_parent=True,
        backref="checked_companies",
    )
