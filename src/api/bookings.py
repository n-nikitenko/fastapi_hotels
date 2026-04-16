from fastapi import APIRouter, Body
from fastapi import HTTPException
from fastapi.openapi.models import Example
from starlette.status import HTTP_409_CONFLICT

from api.dependencies import DbDep, UserIdDep
from exceptions import RoomNotFoundHttpException, ObjectNotFoundException, NoFreeRoomsException
from schemas import BookingAdd
from services import BookingsService

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.post("/", summary="Создание брони")
async def create_booking(
    db: DbDep,
    user_id: UserIdDep,
    booking_data: BookingAdd = Body(
        openapi_examples={
            "1": Example(
                summary="3 ночи",
                value={
                    "room_id": 1,
                    "from_date": "2026-03-01",
                    "to_date": "2026-03-04",
                },
            ),
            "2": Example(
                summary="10 ночей",
                value={
                    "room_id": 2,
                    "from_date": "2026-04-10",
                    "to_date": "2026-04-20",
                },
            ),
        }
    ),
):
    try:
        booking = await BookingsService(db).create(user_id=user_id, booking_data=booking_data)
    except ObjectNotFoundException:
        raise RoomNotFoundHttpException(detail=f"Номер c room_id={booking_data.room_id} не найден")
    except NoFreeRoomsException:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=f"Номер c room_id={booking_data.room_id} уже забронирован",
        )
    else:
        return {"ok": True, "data": booking}


@router.get("/", summary="Список всех бронирований")
async def get_bookings(
    db: DbDep,
):
    return await BookingsService(db).get_all()


@router.get("/me", summary="Список бронирований пользователя")
async def get_user_bookings(
    user_id: UserIdDep,
    db: DbDep,
):
    return await BookingsService(db).get_all_for_user(user_id=user_id)
