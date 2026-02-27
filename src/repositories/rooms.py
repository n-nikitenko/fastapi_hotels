from datetime import date

from sqlalchemy import select, func

from models import RoomOrm, BookingOrm
from repositories.base import BaseRepository
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
        rooms_count_cte = (
            select(
                BookingOrm.room_id,
                func.count().label("rooms_booked")
            )
            .where(
                BookingOrm.from_date <= to_date,
                BookingOrm.to_date >= from_date
            )
            .group_by(BookingOrm.room_id)
            .cte("rooms_count")
        )

        rooms_left_table_cte = (
            select(
                self._model.id.label("room_id"),
               ( self._model.quantity - func.coalesce(rooms_count_cte.c.rooms_booked, 0)).label("rooms_left")
            )
            .outerjoin(rooms_count_cte, self._model.id == rooms_count_cte.c.room_id)
            .cte("rooms_left_table")
        )

        query = (
            select(
                self._model.id,
                self._model.hotel_id,
                self._model.title,
                self._model.description,
                self._model.price,
                rooms_left_table_cte.c.rooms_left.label('quantity')

            )
            .join(rooms_left_table_cte, self._model.id == rooms_left_table_cte.c.room_id)
            .where(
                rooms_left_table_cte.c.rooms_left > 0,
                self._model.hotel_id==hotel_id,
            )
        )

        result = await self._session.execute(query)
        return [self._to_schema(row) for row in result.mappings().all()]