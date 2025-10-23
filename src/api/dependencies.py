from typing import Annotated

from fastapi import Depends
from fastapi.params import Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: Annotated[int | None, Field(), Query(None, ge=1, description="Номер страницы")]
    limit: Annotated[int | None, Query(None, ge=1, lt=30, description="Кол-во отелей на странице")]


PaginationDep = Annotated[PaginationParams, Depends()]