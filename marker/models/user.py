import datetime
from typing import Optional

import argon2
from sqlalchemy import func, select
from sqlalchemy.orm import Mapped, mapped_column, object_session, relationship

from .association import (
    companies_stars,
    projects_stars,
    selected_companies,
    selected_contacts,
    selected_projects,
    selected_tags,
)
from .comment import Comment
from .company import Company
from .contact import Contact
from .meta import Base
from .project import Project
from .tag import Tag

ph = argon2.PasswordHasher()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    fullname: Mapped[str]
    email: Mapped[str]
    role: Mapped[str]
    _password: Mapped[str] = mapped_column("password")
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
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

    companies_stars: Mapped[list["Company"]] = relationship(
        secondary=companies_stars,
        cascade="delete",
        single_parent=True,
    )

    projects_stars: Mapped[list["Project"]] = relationship(
        secondary=projects_stars,
        cascade="delete",
        single_parent=True,
    )

    selected_companies: Mapped[list["Company"]] = relationship(
        secondary=selected_companies,
        cascade="delete",
        single_parent=True,
    )

    selected_projects: Mapped[list["Project"]] = relationship(
        secondary=selected_projects,
        cascade="delete",
        single_parent=True,
    )

    selected_tags: Mapped[list["Tag"]] = relationship(
        secondary=selected_tags,
        cascade="delete",
        single_parent=True,
    )

    selected_contacts: Mapped[list["Contact"]] = relationship(
        secondary=selected_contacts,
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
    def count_contacts(self) -> int:
        return object_session(self).scalar(
            select(func.count()).select_from(Contact).filter(Contact.created_by == self)
        )

    @property
    def count_comments(self) -> int:
        return object_session(self).scalar(
            select(func.count()).select_from(Comment).filter(Comment.created_by == self)
        )
