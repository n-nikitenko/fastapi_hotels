from repositories import HotelRepository


async def hotel_exists(hotel_id: int, repo) -> bool:
    hotel = await repo.get_one_or_none(id=hotel_id)
    return  hotel is not None