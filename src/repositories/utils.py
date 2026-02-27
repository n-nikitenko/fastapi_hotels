from datetime import date

from sqlalchemy import func, select, Select

from models import BookingOrm


def get_available_rooms_by_date_stmt(
        rooms_model,
        from_date: date,
        to_date: date,
        hotel_id: int | None = None,
) -> Select:
    """
    возвращает select запрос для получения свободных номеров в указанный промежуток дат
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
            rooms_model.id.label("room_id"),
            (rooms_model.quantity - func.coalesce(rooms_count_cte.c.rooms_booked, 0)).label("rooms_left")
        )
        .outerjoin(rooms_count_cte, rooms_model.id==rooms_count_cte.c.room_id)
        .cte("rooms_left_table")
    )

    conditions = [rooms_left_table_cte.c.rooms_left > 0]
    if hotel_id is not None:
        conditions.append(rooms_model.hotel_id == hotel_id)

    query = (
        select(
            rooms_model.id,
            rooms_model.hotel_id,
            rooms_model.title,
            rooms_model.description,
            rooms_model.price,
            rooms_left_table_cte.c.rooms_left.label('quantity')

        )
        .join(rooms_left_table_cte, rooms_model.id==rooms_left_table_cte.c.room_id)
        .where(*conditions)
    )

    return query