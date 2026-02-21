from fastapi import APIRouter, Body
from fastapi import HTTPException
from fastapi.openapi.models import Example
from fastapi.params import Query

from api.dependencies import PaginationDep, DbDep
from schemas import HotelAdd, HotelPatch

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("/", summary="Список отелей")
async def get_hotels(
        paginator: PaginationDep,
        db: DbDep,
        title: str | None = Query(
            default=None,
            description="Название отеля"
        ),
        location: str | None = Query(
            default=None,
            description="Адрес отеля"
        ),
):
    limit = paginator.limit or 5
    return await db.hotels.get_all(limit=limit, offset=(paginator.page - 1) * limit, location=location, title=title)


@router.delete("/{id}", summary="Удаление отеля")
async def remove_hotel(
        hotel_id: int,
        db: DbDep,
):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"ok": True}


@router.post("/", summary="Создание отеля")
async def create_hotel(
        db: DbDep,
        hotel_data: HotelAdd = Body(
            openapi_examples={
                "1": Example(
                    summary="Сочи",
                    value={"title": "Отель Сочи у моря", "location": "ул. Моря, 3", "stars": 3}
                ),
                "2": Example(
                    summary="Дубай",
                    value={"title": "Отель Дубай у фонтана", "location": "ул. Фонтана, 13", "stars": 4}
                )
            }
        ),
):
    hotel = await db.hotels.create(hotel_data)
    await db.commit()

    return {"ok": True, "data": hotel}


@router.put("/{hotel_id}", summary="Обновление данных отеля")
async def update_hotel(
        hotel_id: int,
        hotel_data: HotelAdd,
        db: DbDep,
):
    hotel = await db.hotels.update(hotel_data, id=hotel_id)
    await db.commit()
    if hotel:
        return {"ok": True, "hotel": hotel}
    raise HTTPException(status_code=404, detail="Отель не найден")


@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле")
async def patch_hotel(
        hotel_id: int,
        hotel_data: HotelPatch,
        db: DbDep,
):
    hotel = await db.hotels.update(hotel_data, id=hotel_id, exclude_unset=True)
    await db.commit()
    if hotel:
        return {"ok": True, "hotel": hotel}
    raise HTTPException(status_code=404, detail="Отель не найден")


@router.get("/{hotel_id}", summary="Получение данных отеля")
async def get_hotel(
        hotel_id: int,
        db: DbDep,
):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Отель не найден")
    return hotel
