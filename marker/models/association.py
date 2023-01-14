from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    Unicode,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .meta import Base


class CompaniesProjects(Base):
    __tablename__ = "companies_projects"
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    stage: Mapped[str] = mapped_column(Unicode(100))
    role: Mapped[str] = mapped_column(Unicode(100))
    company: Mapped["Company"] = relationship(back_populates="projects")
    project: Mapped["Project"] = relationship(back_populates="companies")


companies_tags = Table(
    "companies_tags",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)


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



############
# TO REMOVE
############

companies_persons = Table(
    "companies_persons",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "person_id",
        Integer,
        ForeignKey("persons.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)

companies_comments = Table(
    "companies_comments",
    Base.metadata,
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "comment_id",
        Integer,
        ForeignKey("comments.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)

projects_persons = Table(
    "projects_persons",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("projects.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "person_id",
        Integer,
        ForeignKey("persons.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)

projects_comments = Table(
    "projects_comments",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("projects.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
    Column(
        "comment_id",
        Integer,
        ForeignKey("comments.id", onupdate="CASCADE", ondelete="CASCADE"),
    ),
)
