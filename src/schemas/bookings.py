from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class BookingAdd(BaseModel):
    room_id: Annotated[int, Field(description="Идентификатор номера")]
    from_date: Annotated[date, Field(description="Дата начала бронирования")]
    to_date: Annotated[date, Field(description="Дата окончания бронирования")]

    @model_validator(mode="after")
    def check_dates(self) -> "BookingAdd":
        if self.to_date <= self.from_date:
            raise ValueError("Дата окончания бронирования должна быть позже даты начала")
        return self

class BookingAddEx(BookingAdd):
    user_id: Annotated[int, Field(description="Идентификатор пользователя")]
    price: Annotated[int, Field(description="Стоимость", gt=0)]

class Booking(BookingAddEx):
    id: Annotated[int | None, Field(default=None, description="Идентификатор")]