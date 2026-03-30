from schemas import HotelAdd

async def test_create_hotel(db):
    hotel_data = HotelAdd(title="hotel 5 stars", location="SOCHI", stars=5)
    await db.hotels.create(hotel_data)
    await db.commit()