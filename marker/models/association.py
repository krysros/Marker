from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .meta import Base


class Activity(Base):
    __tablename__ = "activity"
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    stage: Mapped[Optional[str]]
    role: Mapped[Optional[str]]
    company: Mapped["Company"] = relationship(back_populates="projects")
    project: Mapped["Project"] = relationship(back_populates="companies")


class Themes(Base):
    __tablename__ = "themes"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    theme: Mapped[str]


companies_tags = Table(
    "companies_tags",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)


projects_tags = Table(
    "projects_tags",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("projects.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)


companies_stars = Table(
    "companies_stars",
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

projects_stars = Table(
    "projects_stars",
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

selected_companies = Table(
    "selected_companies",
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

selected_projects = Table(
    "selected_projects",
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

selected_tags = Table(
    "selected_tags",
    Base.metadata,
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)

selected_contacts = Table(
    "selected_contacts",
    Base.metadata,
    Column(
        "contact_id",
        Integer,
        ForeignKey("contacts.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)
