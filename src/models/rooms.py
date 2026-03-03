from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class RoomOrm(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"), index=True)
    title: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[int] = mapped_column(BigInteger)
    quantity: Mapped[int]

    facilities: Mapped[list["FacilityOrm"]] = relationship(secondary="rooms_facilities", back_populates="rooms")