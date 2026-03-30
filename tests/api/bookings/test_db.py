from datetime import date

import pytest

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


async def test_crud(db, test_booking_data):
    # create
    result = await db.bookings.create(test_booking_data)
    assert result.id is not None
    assert result.room_id==test_booking_data.room_id
    assert result.user_id==test_booking_data.user_id
    assert result.from_date==test_booking_data.from_date
    assert result.to_date==test_booking_data.to_date
    assert result.price==test_booking_data.price

    # read
    booking_from_db = await db.bookings.get_one_or_none(id=result.id)
    assert booking_from_db.id==result.id
    assert booking_from_db.room_id==test_booking_data.room_id
    assert booking_from_db.user_id==test_booking_data.user_id
    assert booking_from_db.from_date==test_booking_data.from_date
    assert booking_from_db.to_date==test_booking_data.to_date
    assert booking_from_db.price==test_booking_data.price

    # update
    booking_from_db.from_date = date(2026, 2, 25)
    booking_from_db.price = 30_000
    updated_booking = await db.bookings.update(
        id=booking_from_db.id,
        data=booking_from_db,
    )

    assert updated_booking.id==result.id
    assert updated_booking.room_id==booking_from_db.room_id
    assert updated_booking.user_id==booking_from_db.user_id
    assert updated_booking.from_date==booking_from_db.from_date
    assert updated_booking.to_date==booking_from_db.to_date

    # read
    booking_from_db = await db.bookings.get_one_or_none(id=updated_booking.id)
    assert booking_from_db.id==updated_booking.id
    assert booking_from_db.room_id==updated_booking.room_id
    assert booking_from_db.user_id==updated_booking.user_id
    assert booking_from_db.from_date==updated_booking.from_date
    assert booking_from_db.to_date==updated_booking.to_date
    assert booking_from_db.price==updated_booking.price

    # delete
    await db.bookings.delete(id=updated_booking.id)
    # read
    booking_from_db = await db.bookings.get_one_or_none(id=updated_booking.id)
    assert booking_from_db is None
