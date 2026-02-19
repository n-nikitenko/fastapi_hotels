from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.cyextension.util import Mapping

class RoomAdd(BaseModel):
    title: Annotated[str, Field(description="Название")]
    description: Annotated[str | None, Field(default=None, description="Описание")]
    price: Annotated[int, Field(description="Стоимость", gt=0)]
    quantity: Annotated[int, Field(description="Количество", ge=0)]

class RoomAddEx(RoomAdd):
    hotel_id: Annotated[int, Field(description="Идентификатор отеля")]
    title: Annotated[str, Field(description="Название")]
    description: Annotated[str | None, Field(default=None, description="Описание")]
    price: Annotated[int, Field(description="Стоимость", gt=0)]
    quantity: Annotated[int, Field(description="Количество", ge=0)]

class Room(RoomAdd):
    __tablename__ = "rooms"

    id: Annotated[int | None, Field(default=None, description="Идентификатор")]

class RoomPatch(BaseModel):
    hotel_id: Annotated[int | None, Field(default=None, description="Идентификатор отеля")]
    title: Annotated[str, Field(default=None, description="Название")]
    description: Annotated[str | None, Field(default=None, description="Описание")]
    price: Annotated[int | None, Field(default=None, description="Стоимость", gt=0)]
    quantity: Annotated[int | None, Field(default=None, description="Количество", ge=0)]