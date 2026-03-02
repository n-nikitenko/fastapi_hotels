from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class FacilityOrm(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str]


class RoomFacilityOrm(Base):
    __tablename__ = "rooms_facilities"
    __table_args__ = (
        UniqueConstraint("room_id", "facility_id", name="uq_room_facility"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"), index=True)