from api.dependencies import get_db_manager
from schemas import HotelAdd

async def test_create_hotel():
    hotel_data = HotelAdd(title="hotel 5 stars", location="SOCHI", stars=5)
    async with get_db_manager() as db:
        new_hotel_data = await db.hotels.create(hotel_data)
        print(f"{new_hotel_data=}")