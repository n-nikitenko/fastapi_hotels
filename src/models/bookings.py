from datetime import date

from sqlalchemy import BigInteger, ForeignKey, Date, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base


class BookingOrm(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    from_date: Mapped[date] = mapped_column(Date)
    to_date: Mapped[date] = mapped_column(Date)
    price: Mapped[int] = mapped_column(BigInteger)

    @hybrid_property
    def total_cost(self) -> int:
        return self.price * (self.to_date - self.from_date).days

    @total_cost.expression
    def total_cost(cls) -> int:
        return cls.price * func.date_part("day", cls.to_date - cls.from_date)