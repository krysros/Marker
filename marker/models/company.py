import datetime

from sqlalchemy import (
    ForeignKey,
    Unicode,
    select,
    func,
    and_,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    object_session,
    backref,
)

from slugify import slugify

from .meta import Base
from .tag import Tag
from .tables import (
    CompaniesProjectsAssociation,
    companies_tags,
    companies_persons,
    companies_comments,
    recommended,
)


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(100))
    street: Mapped[str] = mapped_column(Unicode(100))
    postcode: Mapped[str] = mapped_column(Unicode(10))
    city: Mapped[str] = mapped_column(Unicode(100))
    state: Mapped[str] = mapped_column(Unicode(2))
    country: Mapped[str] = mapped_column(Unicode(2))
    latitude: Mapped[float]
    longitude: Mapped[float]
    link: Mapped[str] = mapped_column(Unicode(100))
    NIP: Mapped[str] = mapped_column(Unicode(20))
    REGON: Mapped[str] = mapped_column(Unicode(20))
    KRS: Mapped[str] = mapped_column(Unicode(20))
    court: Mapped[str] = mapped_column(Unicode(100))
    color: Mapped[str] = mapped_column(Unicode(10))
    tags: Mapped[list["Tag"]] = relationship(
        secondary=companies_tags, backref="companies"
    )
    projects: Mapped[list["Project"]] = relationship(
        secondary="companies_projects", backref="companies"
    )
    people: Mapped[list["Person"]] = relationship(
        secondary=companies_persons,
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="select",
        backref=backref("company", uselist=False),
    )
    comments: Mapped[list["Comment"]] = relationship(
        secondary=companies_comments,
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="select",
        backref=backref("company", uselist=False),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    editor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped["User"] = relationship(foreign_keys=[editor_id])

    def __init__(
        self,
        name: str,
        street: str,
        postcode: str,
        city: str,
        state: str,
        country: str,
        link: str,
        NIP: str,
        REGON: str,
        KRS: str,
        court: str,
        color: str,
    ) -> None:
        self.name = name
        self.street = street
        self.postcode = postcode
        self.city = city
        self.state = state
        self.country = country
        self.link = link
        self.NIP = NIP
        self.REGON = REGON
        self.KRS = KRS
        self.court = court
        self.color = color

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def count_projects(self) -> int:
        return object_session(self).scalar(
            select(func.count(CompaniesProjectsAssociation.company_id)).where(
                CompaniesProjectsAssociation.company_id == self.id
            )
        )

    @property
    def count_tags(self) -> int:
        return object_session(self).scalar(
            select(func.count(companies_tags.c.company_id)).where(
                companies_tags.c.company_id == self.id
            )
        )

    @property
    def count_persons(self) -> int:
        return object_session(self).scalar(
            select(func.count(companies_persons.c.company_id)).where(
                companies_persons.c.company_id == self.id
            )
        )

    @property
    def count_comments(self) -> int:
        return object_session(self).scalar(
            select(func.count(companies_comments.c.company_id)).where(
                companies_comments.c.company_id == self.id
            )
        )

    @property
    def count_recommended(self) -> int:
        return object_session(self).scalar(
            select(func.count(recommended.c.company_id)).where(
                recommended.c.company_id == self.id
            )
        )

    @property
    def count_similar(self) -> int:
        return object_session(self).scalar(
            select(func.count())
            .select_from(Company)
            .join(Tag, Company.tags)
            .filter(
                and_(
                    Tag.companies.any(Company.id == self.id),
                    Company.id != self.id,
                )
            )
        )
