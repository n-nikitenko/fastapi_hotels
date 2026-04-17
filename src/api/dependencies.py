from typing import Annotated, AsyncGenerator, Any

from fastapi import Depends, Request
from fastapi.params import Query
from pydantic import BaseModel, Field

from exceptions import UnauthorizedHttpException, InvalidTokenHttpException, InvalidTokenException
from services import AuthService
from utils import DBManager
from repositories import (
    HotelRepository,
    RoomRepository,
    UserRepository,
    BookingRepository,
    FacilityRepository,
    RoomsFacilitiesRepository,
)


class PaginationParams(BaseModel):
    page: Annotated[int, Field(), Query(1, ge=1, description="Номер страницы")]
    limit: Annotated[int | None, Query(None, ge=1, lt=30, description="Кол-во отелей на странице")]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_access_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if access_token:
        return access_token
    raise UnauthorizedHttpException


def get_user_id(access_token: Annotated[str, Depends(get_access_token)]) -> int:
    try:
        data = AuthService.decode_token(access_token)
    except InvalidTokenException:
        raise InvalidTokenHttpException()
    else:
        return data["user_id"]


UserIdDep = Annotated[int, Depends(get_user_id)]


def get_db_manager(session_factory=None) -> DBManager:
    from src.database import session_maker

    if session_factory is None:
        session_factory = session_maker

    return DBManager(
        session_factory,
        hotel_repo_cls=HotelRepository,
        user_repo_cls=UserRepository,
        room_repo_cls=RoomRepository,
        bookings_repo_cls=BookingRepository,
        facilities_repo_cls=FacilityRepository,
        rooms_facilities_repo_cls=RoomsFacilitiesRepository,
    )


async def get_db() -> AsyncGenerator[DBManager, Any]:
    async with get_db_manager() as db:
        yield db


DbDep = Annotated[DBManager, Depends(get_db)]
