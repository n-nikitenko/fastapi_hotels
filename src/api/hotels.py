from datetime import date
from typing import Annotated

from fastapi import APIRouter, Body
from fastapi import HTTPException
from fastapi.openapi.models import Example
from fastapi.params import Query
from starlette.status import HTTP_404_NOT_FOUND

from api.dependencies import PaginationDep, DbDep
from api.utils import raise_if_dates_inconsistency
from exceptions import ObjectNotFoundException
from schemas import HotelAdd, HotelPatch
from services import HotelsService

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("/", summary="Список отелей")
async def get_hotels(
    paginator: PaginationDep,
    db: DbDep,
    from_date: Annotated[date, Query(examples=["2026-04-10"])],
    to_date: Annotated[date, Query(examples=["2026-04-14"])],
    title: Annotated[str | None, Query(description="Название отеля")] = None,
    location: Annotated[str | None, Query(description="Адрес отеля")] = None,
):
    raise_if_dates_inconsistency(from_date, to_date)
    return await HotelsService(db).get_filtered_by_dates(
        limit=paginator.limit,
        page=paginator.page,
        location=location,
        title=title,
        from_date=from_date,
        to_date=to_date,
    )


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
                value={
                    "title": "Отель Сочи у моря",
                    "location": "ул. Моря, 3",
                    "stars": 3,
                },
            ),
            "2": Example(
                summary="Дубай",
                value={
                    "title": "Отель Дубай у фонтана",
                    "location": "ул. Фонтана, 13",
                    "stars": 4,
                },
            ),
        }
    ),
):
    hotel = await HotelsService(db).create(hotel_data)

    return {"ok": True, "data": hotel}


@router.put("/{hotel_id}", summary="Обновление данных отеля")
async def update_hotel(
    hotel_id: int,
    hotel_data: HotelAdd,
    db: DbDep,
):
    try:
        hotel = await HotelsService(db).update(hotel_data=hotel_data, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Отель не найден")
    else:
        return {"ok": True, "hotel": hotel}


@router.patch("/{hotel_id}", summary="Частичное обновление данных об отеле")
async def patch_hotel(
    hotel_id: int,
    hotel_data: HotelPatch,
    db: DbDep,
):
    try:
        hotel = await HotelsService(db).update(hotel_data=hotel_data, hotel_id=hotel_id, exclude_unset=True)
    except ObjectNotFoundException:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Отель не найден")
    else:
        return {"ok": True, "hotel": hotel}


@router.get("/{hotel_id}", summary="Получение данных отеля")
async def get_hotel(
    hotel_id: int,
    db: DbDep,
):
    try:
        hotel = await HotelsService(db).get_one(hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Отель не найден")
    return hotel
