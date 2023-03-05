import datetime
from typing import Optional
from slugify import slugify
from sqlalchemy import ForeignKey, Unicode, and_, func, select
from sqlalchemy.orm import Mapped, mapped_column, object_session, relationship

from .association import CompaniesProjects, companies_tags, recommended
from .comment import Comment
from .meta import Base
from .contact import Contact
from .tag import Tag


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(100))
    street: Mapped[Optional[str]] = mapped_column(Unicode(100))
    postcode: Mapped[Optional[str]] = mapped_column(Unicode(10))
    city: Mapped[Optional[str]] = mapped_column(Unicode(100))
    region: Mapped[Optional[str]] = mapped_column(Unicode(2))
    country: Mapped[Optional[str]] = mapped_column(Unicode(2))
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]
    link: Mapped[Optional[str]] = mapped_column(Unicode(100))
    NIP: Mapped[Optional[str]] = mapped_column(Unicode(20))
    REGON: Mapped[Optional[str]] = mapped_column(Unicode(20))
    KRS: Mapped[Optional[str]] = mapped_column(Unicode(20))
    court: Mapped[Optional[str]] = mapped_column(Unicode(100))
    color: Mapped[Optional[str]] = mapped_column(Unicode(10))

    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    editor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped[Optional["User"]] = relationship(foreign_keys=[editor_id])

    tags: Mapped[list["Tag"]] = relationship(
        secondary=companies_tags, back_populates="companies"
    )
    projects: Mapped[list["CompaniesProjects"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["Contact"]] = relationship(back_populates="company")
    comments: Mapped[list["Comment"]] = relationship(back_populates="company")

    def __init__(
        self,
        name: str,
        street: str,
        postcode: str,
        city: str,
        region: str,
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
        self.region = region
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
    def count_contacts(self) -> int:
        return object_session(self).scalar(
            select(func.count())
            .select_from(Contact)
            .where(Contact.company_id == self.id)
        )

    @property
    def count_comments(self) -> int:
        return object_session(self).scalar(
            select(func.count())
            .select_from(Comment)
            .where(Comment.company_id == self.id)
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
