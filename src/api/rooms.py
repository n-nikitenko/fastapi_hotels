from datetime import date

from fastapi import APIRouter, Body
from fastapi import Query
from fastapi.openapi.models import Example

from api.dependencies import DbDep
from api.utils import raise_if_dates_inconsistency, raise_if_hotel_not_found
from exceptions import ObjectNotFoundException, RoomNotFoundHttpException
from schemas import RoomAdd, RoomPatchRequest
from services import RoomsService

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms/", summary="Список номеров")
async def get_rooms(
    hotel_id: int,
    db: DbDep,
    from_date: date = Query(examples=["2026-04-10"]),
    to_date: date = Query(examples=["2026-04-14"]),
):
    raise_if_dates_inconsistency(from_date, to_date)
    await raise_if_hotel_not_found(hotel_id, db.hotels)
    return await RoomsService(db).get_filtered_by_date(
        hotel_id=hotel_id, from_date=from_date, to_date=to_date
    )


@router.delete("/{hotel_id}/rooms/{id}", summary="Удаление")
async def remove_room(
    hotel_id: int,
    room_id: int,
    db: DbDep,
):
    await raise_if_hotel_not_found(hotel_id, db.hotels)
    try:
        await RoomsService(db).remove(room_id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHttpException()
    else:
        return {"ok": True}


@router.post("/{hotel_id}/rooms/", summary="Создание")
async def create_room(
    hotel_id: int,
    db: DbDep,
    room_data: RoomAdd = Body(
        openapi_examples={
            "1": Example(
                summary="SGL",
                value={
                    "title": "Одноместный",
                    "description": "Предназначен для размещения одного человека и комплектуется одной кроватью.",
                    "price": 6000,
                    "quantity": 300,
                },
            ),
            "2": Example(
                summary="DBL",
                value={
                    "title": "Двухместный с одной кроватью",
                    "description": " Предусматривает установку одной двуспальной кровати и проживание "
                    "двух постояльцев.",
                    "price": 12000,
                    "quantity": 150,
                },
            ),
        }
    ),
):
    await raise_if_hotel_not_found(hotel_id, db.hotels)
    room = await RoomsService(db).create(hotel_id=hotel_id, room_data=room_data)

    return {"ok": True, "data": room}


@router.put("/{hotel_id}/rooms/{room_id}", summary="Обновление данных")
async def update_room(
    hotel_id: int,
    room_id: int,
    room_data: RoomAdd,
    db: DbDep,
):
    await raise_if_hotel_not_found(hotel_id, db.hotels)
    try:
        room = await RoomsService(db).update(
            room_data=room_data,
            room_id=room_id,
            hotel_id=hotel_id,
        )
    except ObjectNotFoundException:
        raise RoomNotFoundHttpException()
    else:
        return {"ok": True, "room": room}


@router.patch("/{hotel_id}/rooms/{room_id}", summary="Частичное обновление данных")
async def patch_room(
    hotel_id: int,
    room_id: int,
    room_data: RoomPatchRequest,
    db: DbDep,
):
    await raise_if_hotel_not_found(hotel_id, db.hotels)
    if room_data.hotel_id:
        await raise_if_hotel_not_found(room_data.hotel_id, db.hotels)
    else:
        room_data.hotel_id = hotel_id
    try:
        room = await RoomsService(db).update(
            room_data=room_data,
            room_id=room_id,
            hotel_id=hotel_id,
            exclude_unset=True,
        )
    except ObjectNotFoundException:
        raise RoomNotFoundHttpException()
    else:
        return {"ok": True, "room": room}


@router.get("/{hotel_id}/rooms/{room_id}", summary="Получение данных")
async def get_room(
    hotel_id: int,
    room_id: int,
    db: DbDep,
):
    await raise_if_hotel_not_found(hotel_id, db.hotels)
    try:
        room = await RoomsService(db).get(room_id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHttpException()
    else:
        return room
