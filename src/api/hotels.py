from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.params import Query

from api.dependencies import PaginationDep
from schemas import Hotel, HotelPatch

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


@router.get("/")
async def get_hotels(
        paginator: PaginationDep,
        hotel_id: int | None = Query(default=None),
        title: str | None = Query(default=None, description="Название отеля")
):
    ret = hotels
    if hotel_id or title:
        ret = [hotel for hotel in hotels if hotel["id"]==hotel_id or hotel["title"]==title]
    start_idx = (abs(paginator.page) - 1) * abs(paginator.limit)
    return ret[start_idx: start_idx + abs(paginator.limit)]


@router.delete("/{id}")
async def remove_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"]!=hotel_id]


@router.post("/")
async def create_hotel(hotel_data: Hotel):
    global hotels
    hotels.append({"id": len(hotels) + 1, "title": hotel_data.title, "stars": hotel_data.stars})
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
