from fastapi import APIRouter, Body
from fastapi import HTTPException
from fastapi.openapi.models import Example
from fastapi.params import Query

from api.dependencies import PaginationDep
from database import session_maker
from models import HotelOrm
from schemas import Hotel, HotelPatch
from sqlalchemy import insert, select, or_

router = APIRouter(prefix="/hotels", tags=["Отели"])

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "dubai"},
    {"id": 3, "title": "Мальдивы", "name": "maldivi"},
    {"id": 4, "title": "Геленджик", "name": "gelendzhik"},
    {"id": 5, "title": "Москва", "name": "moscow"},
    {"id": 6, "title": "Казань", "name": "kazan"},
    {"id": 7, "title": "Санкт-Петербург", "name": "spb"},
]


@router.get("/", summary="Список отелей")
async def get_hotels(
        paginator: PaginationDep,
        title: str | None = Query(default=None, description="Название отеля"),
        location: str | None = Query(default=None, description="Адрес отеля"),
):
    limit = paginator.limit or 5
    async with session_maker() as session:
        query = select(HotelOrm)
        filters = []
        if location:
            filters.append(HotelOrm.location.icontains(location))
        if title:
            filters.append(HotelOrm.title.icontains(title))

        if filters:
            query = query.where(or_(*filters))
        query = (
            query
            .offset((paginator.page - 1) * limit)
            .limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()


@router.delete("/{id}")
async def remove_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"]!=hotel_id]


@router.post("/", summary="Создание отеля")
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": Example(
        summary="Сочи",
        value={
            "title": "Отель Сочи у моря",
            "location": "ул. Моря, 3",
            "stars": 3
        }),
    "2": Example(
            summary="Дубай",
            value={
                "title": "Отель Дубай у фонтана",
                "location": "ул. Фонтана, 13",
                "stars": 4
            })
})):
    async with session_maker() as session:
        stmt = insert(HotelOrm).values(**hotel_data.model_dump())
        await session.execute(stmt)
        await session.commit()

    return {"ok": True}


@router.put("/{hotel_id}")
async def update_hotel(
        hotel_id: int,
        hotel_data: Hotel
):
    global hotels
    hotel = next((hotel for hotel in hotels if hotel["id"]==hotel_id), None)
    if hotel:
        hotel.update({"title": hotel_data.title, "stars": hotel_data.stars})
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Отель не найден")


@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле"
)
async def patch_hotel(
        hotel_id: int,
        hotel_data: HotelPatch
):
    global hotels
    hotel = next((hotel for hotel in hotels if hotel["id"]==hotel_id), None)
    if hotel:
        if hotel_data.title:
            hotel.update({"title": hotel_data.title})
        if hotel_data.stars:
            hotel.update({"stars": hotel_data.stars})
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Отель не найден")
