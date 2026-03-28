from api.dependencies import get_db_manager
from database import session_maker_null_pool
from schemas import HotelAdd


async def test_create_hotel():
    hotel_data = HotelAdd(title="hotel 5 stars", location="SOCHI", stars=5)
    async with get_db_manager(session_factory=session_maker_null_pool) as db:
        await db.hotels.create(hotel_data)
        await db.commit()