import typing

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if typing.TYPE_CHECKING:
    from .rooms import RoomOrm


class FacilityOrm(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str]

    rooms: Mapped[list["RoomOrm"]] = relationship(
        secondary="rooms_facilities", back_populates="facilities"
    )


class RoomFacilityOrm(Base):
    __tablename__ = "rooms_facilities"
    __table_args__ = (UniqueConstraint("room_id", "facility_id", name="uq_room_facility"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"), index=True)
