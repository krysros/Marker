import datetime

import argon2
from sqlalchemy import Unicode, func, select
from sqlalchemy.orm import Mapped, mapped_column, object_session, relationship

from .association import checked, recommended, watched
from .comment import Comment
from .company import Company
from .meta import Base
from .person import Person
from .project import Project
from .tag import Tag

ph = argon2.PasswordHasher()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(30), unique=True)
    fullname: Mapped[str] = mapped_column(Unicode(50))
    email: Mapped[str] = mapped_column(Unicode(50))
    role: Mapped[str] = mapped_column(Unicode(20))
    _password: Mapped[str] = mapped_column("password", Unicode(255))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    @property
    def password(self) -> None:
        return self._password

    @password.setter
    def password(self, pw: str) -> str:
        self._password = ph.hash(pw)

    def check_password(self, pw: str) -> bool:
        try:
            ph.verify(self.password, pw)
            if ph.check_needs_rehash(self.password):
                self.password = pw
            return True
        except argon2.exceptions.VerifyMismatchError as error:
            return False

    recommended: Mapped[list["Company"]] = relationship(
        secondary=recommended,
        cascade="delete",
        single_parent=True,
    )

    watched: Mapped[list["Project"]] = relationship(
        secondary=watched,
        cascade="delete",
        single_parent=True,
    )

    checked: Mapped[list["Company"]] = relationship(
        secondary=checked,
        cascade="delete",
        single_parent=True,
    )

    @property
    def count_companies(self) -> int:
        return object_session(self).scalar(
            select(func.count()).select_from(Company).filter(Company.created_by == self)
        )

    @property
    def count_projects(self) -> int:
        return object_session(self).scalar(
            select(func.count()).select_from(Project).filter(Project.created_by == self)
        )

    @property
    def count_tags(self) -> int:
        return object_session(self).scalar(
            select(func.count()).select_from(Tag).filter(Tag.created_by == self)
        )

    @property
    def count_persons(self) -> int:
        return object_session(self).scalar(
            select(func.count()).select_from(Person).filter(Person.created_by == self)
        )

    @property
    def count_comments(self) -> int:
        return object_session(self).scalar(
            select(func.count()).select_from(Comment).filter(Comment.created_by == self)
        )
