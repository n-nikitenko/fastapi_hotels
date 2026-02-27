from datetime import date


from models import RoomOrm
from .base import BaseRepository
from .utils import get_available_rooms_by_date_stmt
from schemas import Room


class RoomRepository(BaseRepository):
    _model = RoomOrm
    _schema = Room

    async def get_filtered_by_date(
            self,
            hotel_id: int,
            from_date: date,
            to_date: date,
    ):
        """
        возвращает список свободных номеров в заданном отеле в указанный промежуток дат
        """

        query = get_available_rooms_by_date_stmt(
            rooms_model=self._model,
            hotel_id=hotel_id,
            from_date=from_date,
            to_date=to_date,
        )

        result = await self._session.execute(query)
        return [self._to_schema(row) for row in result.mappings().all()]