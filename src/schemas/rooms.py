from typing import Annotated, List

from pydantic import BaseModel, Field

from .facilities import Facility


class RoomBase(BaseModel):
    title: Annotated[str, Field(description="Название")]
    description: Annotated[str | None, Field(default=None, description="Описание")]
    price: Annotated[int, Field(description="Стоимость", gt=0)]
    quantity: Annotated[int, Field(description="Количество", ge=0)]


class RoomAdd(RoomBase):
    facilities_ids: Annotated[List[int] | None, Field(default=None, description="Удобства")]


class RoomAddEx(RoomBase):
    hotel_id: Annotated[int, Field(description="Идентификатор отеля")]


class Room(RoomBase):
    id: Annotated[int | None, Field(default=None, description="Идентификатор")]
    hotel_id: Annotated[int, Field(description="Идентификатор отеля")]


class RoomWithRels(Room):
    facilities: Annotated[list[Facility], Field(default_factory=list, description="Удобства")]


class RoomPatch(BaseModel):
    hotel_id: Annotated[int | None, Field(default=None, description="Идентификатор отеля")]
    title: Annotated[str | None, Field(default=None, description="Название")]
    description: Annotated[str | None, Field(default=None, description="Описание")]
    price: Annotated[int | None, Field(default=None, description="Стоимость", gt=0)]
    quantity: Annotated[int | None, Field(default=None, description="Количество", ge=0)]


class RoomPatchRequest(RoomPatch):
    facilities_ids: Annotated[List[int] | None, Field(default=None, description="Удобства")]
