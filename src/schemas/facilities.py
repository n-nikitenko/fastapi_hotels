from typing import Annotated

from pydantic import BaseModel, Field

class FacilityAdd(BaseModel):
    title: Annotated[str, Field(description="Название")]

class Facility(FacilityAdd):
    id: Annotated[int | None, Field(default=None, description="Идентификатор")]


class RoomFacilityAdd(BaseModel):
    room_id: Annotated[int, Field(description="Идентификатор комнаты")]
    facility_id: Annotated[int, Field(description="Идентификатор удобства")]


class RoomFacility(RoomFacilityAdd):
    id: Annotated[int | None, Field(default=None, description="Идентификатор")]