from datetime import date

from exceptions import ObjectNotFoundException
from schemas import HotelAdd, HotelPatch
from .base import BaseService


async def hotel_exists(hotel_id: int, repo) -> bool:
    hotel = await repo.get_one_or_none(id=hotel_id)
    return hotel is not None

_DEFAULT_PAGE_LIMIT =  5

class HotelsService(BaseService):
    async def get_filtered_by_dates(
            self,
            from_date: date,
            to_date: date,
            limit: int | None = None,
            page: int = 1,
            location: str | None = None,
            title: str | None = None
    ):
        assert self.db is not None
        limit = limit or _DEFAULT_PAGE_LIMIT

        return await self.db.hotels.get_all(
            limit=limit,
            offset=(page - 1) * limit,
            location=location,
            title=title,
            from_date=from_date,
            to_date=to_date,
        )

    async def get_one(self, hotel_id: int):
        assert self.db is not None
        return await self.db.hotels.get_one(id=hotel_id)

    async def create(self, hotel_data: HotelAdd):
        assert self.db is not None
        hotel = await self.db.hotels.create(hotel_data)
        await self.db.commit()
        return hotel


    async def update(
            self,
            hotel_id: int,
            hotel_data: HotelAdd | HotelPatch,
            exclude_unset: bool = False,
    ):
        assert self.db is not None
        hotel = await self.db.hotels.update(hotel_data, id=hotel_id, exclude_unset=exclude_unset)
        await self.db.commit()
        if not hotel:
            raise ObjectNotFoundException
        return hotel