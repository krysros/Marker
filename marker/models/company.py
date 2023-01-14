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
)

from slugify import slugify

from .meta import Base
from .tag import Tag
from .person import Person
from .comment import Comment
from .association import (
    CompaniesProjects,
    companies_tags,
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

    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    editor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped["User"] = relationship(foreign_keys=[editor_id])

    tags: Mapped[list["Tag"]] = relationship(
        secondary=companies_tags, back_populates="companies"
    )
    projects: Mapped[list["CompaniesProjects"]] = relationship(back_populates="company")

    people: Mapped[list["Person"]] = relationship(back_populates="company")
    comments: Mapped[list["Comment"]] = relationship(back_populates="company")


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
            select(func.count(CompaniesProjects.company_id)).where(
                CompaniesProjects.company_id == self.id
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
            select(func.count()).select_from(Person).where(
                Person.company_id == self.id
            )
        )

    @property
    def count_comments(self) -> int:
        return object_session(self).scalar(
            select(func.count()).select_from(Comment).where(
                Comment.company_id == self.id
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
