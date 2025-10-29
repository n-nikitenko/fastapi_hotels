from typing import Annotated

from pydantic import BaseModel, Field


class Hotel(BaseModel):
    title: Annotated[str, Field(description="Название отеля")]
    location: Annotated[str, Field(description="Адрес отеля")]
    stars: Annotated[int, Field(description="Количество звезд", le=5, gt=0)]


class HotelPatch(BaseModel):
    title: Annotated[str | None, Field(default=None, description="Название отеля")]
    location: Annotated[str, Field(description="Адрес отеля")]
    stars: Annotated[int | None, Field(default=None, description="Количество звезд", le=5, gt=0)]