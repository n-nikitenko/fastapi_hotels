from datetime import date

import pytest

from api.dependencies import get_db_manager
from database import session_maker_null_pool
from schemas import BookingAddEx


@pytest.fixture()
async def test_booking_data(db) -> BookingAddEx:
    user = (await db.users.get_all())[0]
    room = (await db.rooms.get_all())[0]
    from_date = date(year=2026, month=3, day=1)
    to_date = date(year=2026, month=3, day=4)
    return BookingAddEx(
        room_id=room.id,
        from_date=from_date,
        to_date=to_date,
        user_id=user.id,
        price=6000,
    )


@pytest.fixture(scope="module")
async def remove_all_bookings():
    async with get_db_manager(session_factory=session_maker_null_pool) as db:
        await db.bookings.delete()
        await db.commit()
