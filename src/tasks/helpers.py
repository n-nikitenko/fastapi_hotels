from database import session_maker_null_pool


async def get_bookings_with_today_checkin_helper():
    from api.dependencies import get_db_manager
    print("get_bookings_with_today_checkin_helper started")
    async with get_db_manager(session_maker_null_pool) as db:
        bookings = await db.bookings.get_with_today_checkin()
        print(f"{bookings=}")
