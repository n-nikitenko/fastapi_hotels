from datetime import date

from sqlalchemy import select, or_

from models import HotelOrm, RoomOrm
from repositories.base import BaseRepository
from .utils import get_available_rooms_by_date_stmt
from schemas import Hotel


class HotelRepository(BaseRepository):
    _model = HotelOrm
    _schema = Hotel
    _rooms_model = RoomOrm

    async def get_all(self,
                limit: int,
                offset: int,
                from_date: date,
                to_date: date,
                location: str | None = None,
                title: str | None = None,
                ):
        query = select(self._model)

        available_rooms_cte = (
            get_available_rooms_by_date_stmt(
                rooms_model=self._rooms_model,
                from_date=from_date,
                to_date=to_date,
            )
        ).cte("available_rooms")

        hotels_ids = (
            select(available_rooms_cte.c.hotel_id)
            .distinct()
        )

        filters = [self._model.id.in_(hotels_ids)]
        if location:
            filters.append(self._model.location.ilike(f"%{location}%"))
        if title:
            filters.append(self._model.title.ilike(f"%{title}%"))

        query = (
            query
            .where(or_(*filters))
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.execute(query)
        return [self._to_schema(obj) for obj in result.scalars().all()]