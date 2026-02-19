from fastapi import APIRouter, Body
from fastapi import HTTPException
from fastapi.openapi.models import Example

from database import session_maker
from repositories import RoomRepository, HotelRepository
from schemas import RoomAdd, RoomPatch, RoomAddEx
from services import hotel_exists

router = APIRouter(prefix="/hotels", tags=["Номера"])

async def raise_if_hotel_not_found(hotel_id: int, session):
    if not await hotel_exists(hotel_id, session):
        raise HTTPException(status_code=404, detail=f"Отель c {hotel_id=} не найден")

@router.get("/{hotel_id}/rooms/", summary="Список номеров")
async def get_hotels(hotel_id: int,):
    async with session_maker() as session:
        repo = RoomRepository(session)
        return await repo.get_all_filtered(hotel_id=hotel_id)


@router.delete("/{hotel_id}/rooms/{id}", summary="Удаление")
async def remove_room(hotel_id: int, room_id: int):
    async with session_maker() as session:
        repo = RoomRepository(session)
        await repo.delete(id=room_id, hotel_id=hotel_id)
        await session.commit()
    return {"ok": True}


@router.post("/{hotel_id}/rooms/", summary="Создание")
async def create_room(hotel_id: int, room_data: RoomAdd = Body(openapi_examples={
    "1": Example(
        summary="SGL",
        value={
            "title": "Одноместный",
            "description": "Предназначен для размещения одного человека и комплектуется одной кроватью.",
            "price": 6000,
            "quantity":300,
        }),
    "2": Example(
        summary="DBL",
        value={
            "title": "Двухместный с одной кроватью",
            "description": " Предусматривает установку одной двуспальной кровати и проживание двух постояльцев.",
            "price": 12000,
            "quantity": 150,
        })
})):
    async with session_maker() as session:
        await raise_if_hotel_not_found(hotel_id, session)
        repo = RoomRepository(session)
        new_room = room_data.model_dump()
        new_room["hotel_id"] = hotel_id
        room =  await repo.create(RoomAddEx.model_validate(new_room))
        await session.commit()

    return {"ok": True, "data": room}


@router.put("/{hotel_id}/rooms/{room_id}", summary="Обновление данных")
async def update_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomAddEx
):
    async with session_maker() as session:
        await raise_if_hotel_not_found(hotel_id, session)
        await raise_if_hotel_not_found(room_data.hotel_id, session)
        repo = RoomRepository(session)
        room =  await repo.update(room_data, id=room_id, hotel_id=hotel_id)
        await session.commit()
    if room:
        return {"ok": True , "room": room}
    raise HTTPException(status_code=404, detail="Номер не найден")


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частичное обновление данных"
)
async def patch_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomPatch
):
    async with session_maker() as session:
        await raise_if_hotel_not_found(hotel_id, session)
        if room_data.hotel_id:
            await raise_if_hotel_not_found(room_data.hotel_id, session)
        repo = RoomRepository(session)
        room = await repo.update(room_data, id=room_id, hotel_id=hotel_id, exclude_unset=True)
        await session.commit()
    if room:
        return {"ok": True, "room": room}
    raise HTTPException(status_code=404, detail="Номер не найден")


@router.get("/{hotel_id}/rooms/{room_id}", summary="Получение данных")
async def get_room(
        hotel_id: int,
        room_id: int,
):
    async with session_maker() as session:
        await raise_if_hotel_not_found(hotel_id, session)
        repo = RoomRepository(session)
        hotel = await repo.get_one_or_none(id=room_id, hotel_id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Номер не найден")
    return hotel