from datetime import date

from sqlalchemy import select

from models import RoomOrm
from repositories.base import BaseRepository
from .mappers import HotelDataMapper
from .utils import get_available_rooms_by_date_stmt


class HotelRepository(BaseRepository):
    _mapper = HotelDataMapper
    _rooms_model = RoomOrm

    async def get_all(
        self,
        limit: int,
        offset: int,
        from_date: date,
        to_date: date,
        location: str | None = None,
        title: str | None = None,
    ):
        assert self._mapper.db_model is not None

        query = select(self._mapper.db_model)

        available_rooms_cte = (
            get_available_rooms_by_date_stmt(
                rooms_model=self._rooms_model,
                from_date=from_date,
                to_date=to_date,
            )
        ).cte("available_rooms")

        hotels_ids = select(available_rooms_cte.c.hotel_id).distinct()

        filters = [self._mapper.db_model.id.in_(hotels_ids)]
        if location:
            filters.append(self._mapper.db_model.location.ilike(f"%{location}%"))
        if title:
            filters.append(self._mapper.db_model.title.ilike(f"%{title}%"))

        query = query.where(*filters).offset(offset).limit(limit)

        result = await self._session.execute(query)
        return [self._mapper.to_domain_entity(obj) for obj in result.scalars().all()]
