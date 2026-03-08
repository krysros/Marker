from typing import Optional

from sqlalchemy import Column, ForeignKey, Index, Integer, Table
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
        index=True,
    ),
)


projects_tags = Table(
    "projects_tags",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("projects.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
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


Index(
    "ix_selected_companies_user_company",
    selected_companies.c.user_id,
    selected_companies.c.company_id,
)

Index(
    "ix_selected_projects_user_project",
    selected_projects.c.user_id,
    selected_projects.c.project_id,
)

Index(
    "ix_selected_tags_user_tag",
    selected_tags.c.user_id,
    selected_tags.c.tag_id,
)

Index(
    "ix_selected_contacts_user_contact",
    selected_contacts.c.user_id,
    selected_contacts.c.contact_id,
)
