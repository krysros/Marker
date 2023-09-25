import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .meta import Base


class IdentificationNumber(Base):
    __tablename__ = "identification_numbers"
    id: Mapped[int] = mapped_column(primary_key=True)
    NIP: Mapped[Optional[str]]
    REGON: Mapped[Optional[str]]
    KRS: Mapped[Optional[str]]
    court: Mapped[Optional[str]]

    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    creator_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    editor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    created_by: Mapped["User"] = relationship(foreign_keys=[creator_id])
    updated_by: Mapped[Optional["User"]] = relationship(foreign_keys=[editor_id])

    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship(back_populates="identification_number")

    def __init__(self, NIP: str, REGON: str, KRS: str, court: str) -> None:
        self.NIP = NIP
        self.REGON = REGON
        self.KRS = KRS
        self.court = court
