from fastapi import APIRouter, Body
from fastapi import HTTPException
from fastapi.openapi.models import Example

from api.dependencies import DbDep, UserIdDep
from schemas import BookingAdd, BookingAddEx

router = APIRouter(prefix="/bookings", tags=["Бронирования"])

async def raise_if_room_not_found(room_id: int, repo):
    if not await repo.get_one_or_none(id=room_id):
        raise HTTPException(status_code=404, detail=f"Номер c {room_id=} не найден")

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
                        "from_date": "2026-03-01T14:00:00",
                        "to_date": "2026-03-04T12:00:00",
                    },
                ),
                "2": Example(
                    summary="10 ночей",
                    value={
                        "room_id": 2,
                        "from_date": "2026-04-10T14:00:00",
                        "to_date": "2026-04-20T12:00:00",
                    },
                )
            }
        )
):
    room =  await db.rooms.get_one_or_none(id=booking_data.room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Номер c room_id={booking_data.room_id} не найден")
    if await db.bookings.room_is_busy(booking_data.room_id, booking_data.from_date, booking_data.to_date):
        raise HTTPException(status_code=404, detail=f"Номер c room_id={booking_data.room_id} уже забронирован")
    new_booking = booking_data.model_dump()
    new_booking["user_id"] = user_id
    new_booking["price"] = room.price
    booking =  await db.bookings.create(BookingAddEx.model_validate(new_booking))
    await db.commit()

    return {"ok": True, "data": booking}