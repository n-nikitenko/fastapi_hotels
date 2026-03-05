from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import RoomOrm
from .base import BaseRepository
from .mappers import RoomDataMapper
from .utils import get_available_rooms_by_date_stmt
from schemas import RoomWithRels


class RoomRepository(BaseRepository):
    _model = RoomOrm
    _mapper = RoomDataMapper

    async def get_filtered_by_date(
            self,
            hotel_id: int,
            from_date: date,
            to_date: date,
    ):
        """
        возвращает список свободных номеров в заданном отеле в указанный промежуток дат
        """

        query = (
            get_available_rooms_by_date_stmt(
                rooms_model=self._model,
                hotel_id=hotel_id,
                from_date=from_date,
                to_date=to_date,
            )
            .options(joinedload(self._model.facilities))
        )

        result = await self._session.execute(query)

        items = []
        for room_obj, rooms_left in result.unique().all():
            item = self._mapper.to_domain_entity(room_obj, schema=RoomWithRels)
            item.quantity = rooms_left
            items.append(item)

        return items


    async def get_one_or_none_with_rels(self, **filter_by):
        query = (
            select(self._model)
            .filter_by(**filter_by)
            .options(joinedload(self._model.facilities))
        )

        result = await self._session.execute(query)
        obj = result.scalars().unique().one_or_none()
        return self._mapper.to_domain_entity(obj, schema=RoomWithRels)  if obj else None