from datetime import date

from fastapi import APIRouter, Body
from fastapi import HTTPException, Query
from fastapi.openapi.models import Example
from starlette.status import HTTP_404_NOT_FOUND

from api.dependencies import DbDep
from api.utils import raise_if_dates_inconsistency
from exceptions import ObjectNotFoundException
from schemas import RoomAdd, RoomPatch, RoomAddEx, RoomFacilityAdd, RoomPatchRequest
from services import hotel_exists

router = APIRouter(prefix="/hotels", tags=["Номера"])


async def raise_if_hotel_not_found(hotel_id: int, repo):
    if not await hotel_exists(hotel_id, repo):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Отель c {hotel_id=} не найден")

def _raise_404() -> None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Номер не найден")


@router.get("/{hotel_id}/rooms/", summary="Список номеров")
async def get_rooms(
    hotel_id: int,
    db: DbDep,
    from_date: date = Query(examples=["2026-04-10"]),
    to_date: date = Query(examples=["2026-04-14"]),
):
    raise_if_dates_inconsistency(from_date, to_date)
    await raise_if_hotel_not_found(hotel_id, db.hotels)
    return await db.rooms.get_filtered_by_date(
        hotel_id=hotel_id, from_date=from_date, to_date=to_date
    )


@router.delete("/{hotel_id}/rooms/{id}", summary="Удаление")
async def remove_room(
    hotel_id: int,
    room_id: int,
    db: DbDep,
):
    try:
        await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
       _raise_404()
    else:
        await db.commit()
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
    new_room = room_data.model_dump()
    new_room["hotel_id"] = hotel_id
    room = await db.rooms.create(RoomAddEx.model_validate(new_room))
    if room_data.facilities_ids:
        await db.rooms_facilities.bulk_create(
            [
                RoomFacilityAdd(room_id=room.id, facility_id=facility_id)
                for facility_id in room_data.facilities_ids
            ]
        )
    await db.commit()

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
        room = await db.rooms.update(
            RoomAddEx.model_validate(room_data.model_dump(exclude={"facilities_ids"}) | {"hotel_id": hotel_id}),
            id=room_id,
            hotel_id=hotel_id,
        )
    except ObjectNotFoundException:
        _raise_404()
    else:
        await db.rooms_facilities.sync_room_facilities(
            room_id=room.id,
            facility_ids=room_data.facilities_ids,
        )
        await db.commit()
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
        room = await db.rooms.update(
            RoomPatch.model_validate(
                room_data.model_dump(exclude={"facilities_ids"}, exclude_unset=True)
            ),
            id=room_id,
            hotel_id=hotel_id,
            exclude_unset=True,
        )
    except ObjectNotFoundException:
        _raise_404()
    else:
        if room_data.facilities_ids is not None:
            await db.rooms_facilities.sync_room_facilities(
                room_id=room.id,
                facility_ids=room_data.facilities_ids,
            )
        await db.commit()
        return {"ok": True, "room": room}



@router.get("/{hotel_id}/rooms/{room_id}", summary="Получение данных")
async def get_room(
    hotel_id: int,
    room_id: int,
    db: DbDep,
):
    await raise_if_hotel_not_found(hotel_id, db.hotels)
    try:
        room = await db.rooms.get_one_with_rels(id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        _raise_404()
    else:
        return room
