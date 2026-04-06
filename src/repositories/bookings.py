from datetime import date


from models import RoomOrm
from repositories.base import BaseRepository
from repositories.mappers import BookingDataMapper
from repositories.utils import get_available_rooms_by_date_stmt


class BookingRepository(BaseRepository):
    _mapper = BookingDataMapper
    _rooms_model = RoomOrm

    async def room_is_busy(self, room_id, from_date, to_date, hotel_id):
        query = get_available_rooms_by_date_stmt(
            rooms_model=self._rooms_model,
            from_date=from_date,
            to_date=to_date,
            hotel_id=hotel_id,
        )
        result = await self._session.execute(query)
        for room_obj, rooms_left in result.unique().all():
            if room_obj.id == room_id:
                return rooms_left == 0
        return True

    async def get_with_today_checkin(self):
        return await self.get_all_filtered(from_date=date.today())
