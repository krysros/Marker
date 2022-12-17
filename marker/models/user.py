import datetime

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    DateTime,
    select,
    func,
)

from sqlalchemy.orm import (
    relationship,
    object_session,
)

from .meta import Base
from .company import Company
from .project import Project
from .tag import Tag
from .person import Person
from .comment import Comment
from .tables import (
    checked,
    recommended,
    watched,
)

import argon2

ph = argon2.PasswordHasher()


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

    @property
    def count_companies(self):
        return object_session(self).scalar(
            select(func.count()).select_from(Company).filter(Company.created_by == self)
        )

    @property
    def count_projects(self):
        return object_session(self).scalar(
            select(func.count()).select_from(Project).filter(Project.created_by == self)
        )

    @property
    def count_tags(self):
        return object_session(self).scalar(
            select(func.count()).select_from(Tag).filter(Tag.created_by == self)
        )

    @property
    def count_persons(self):
        return object_session(self).scalar(
            select(func.count()).select_from(Person).filter(Person.created_by == self)
        )

    @property
    def count_comments(self):
        return object_session(self).scalar(
            select(func.count()).select_from(Comment).filter(Comment.created_by == self)
        )
