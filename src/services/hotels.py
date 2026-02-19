from repositories import HotelRepository


async def hotel_exists(hotel_id: int, session) -> bool:
    repo = HotelRepository(session)
    hotel = await repo.get_one_or_none(id=hotel_id)
    return  hotel is not None