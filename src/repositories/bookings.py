from sqlalchemy import select, func

from models import BookingOrm
from repositories.base import BaseRepository
from schemas import Booking


class BookingRepository(BaseRepository):
    _model = BookingOrm
    _schema = Booking

    async def room_is_busy(self, room_id, from_date, to_date):
        query = (
            select(func.count(self._model.id))
            .where(
                self._model.room_id==room_id,
                # диапазоны пересекаются, если:
                # existing.from_date < new_to_date
                # и existing.to_date > new_from_date
                self._model.from_date < to_date,
                self._model.to_date > from_date,
            )
        )
        res = await self._session.execute(query)
        count = res.scalar_one()
        return count > 0