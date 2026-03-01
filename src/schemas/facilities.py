from typing import Annotated

from pydantic import BaseModel, Field

class FacilityAdd(BaseModel):
    title: Annotated[str, Field(description="Название")]

class FacilityAddEx(FacilityAdd):
    room_id: Annotated[int, Field(description="Идентификатор комнаты")]

class Facility(FacilityAdd):
    id: Annotated[int | None, Field(default=None, description="Идентификатор")]