from sqlalchemy import select, or_

from models import HotelOrm
from repositories.base import BaseRepository
from schemas import Hotel


class HotelRepository(BaseRepository):
    _model = HotelOrm
    _schema = Hotel

    async def get_all(self,
                limit: int,
                offset: int,
                location: str | None = None,
                title: str | None = None,
                ):
        query = select(self._model)
        filters = []
        if location:
            filters.append(self._model.location.icontains(location))
        if title:
            filters.append(self._model.title.icontains(title))

        if filters:
            query = query.where(or_(*filters))
        query = (
            query
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return [self._to_schema(obj) for obj in result.scalars().all()]