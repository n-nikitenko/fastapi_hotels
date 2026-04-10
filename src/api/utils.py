from datetime import date

from fastapi import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT

from exceptions import HotelNotFoundHttpException, RoomNotFoundHttpException
from services import hotel_exists


def raise_if_dates_inconsistency(from_date: date, to_date: date) -> None:
    if to_date < from_date:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Дата выезда не может быть раньше даты заезда",
        )


async def raise_if_hotel_not_found(hotel_id: int, repo):
    if not await hotel_exists(hotel_id, repo):
        raise HotelNotFoundHttpException()


async def raise_if_room_not_found(room_id: int, repo):
    if not await repo.get_one_or_none(id=room_id):
        raise RoomNotFoundHttpException(detail=f"Номер c {room_id=} не найден")
