from exceptions import NoFreeRoomsException, ObjectNotFoundException
from schemas import BookingAddEx, BookingAdd, Booking
from services.base import BaseService


class BookingsService(BaseService):
    async def create(
        self,
        user_id: int,
        booking_data: BookingAdd,
    ) -> Booking:
        assert self.db is not None
        room = await self.db.rooms.get_one_or_none(id=booking_data.room_id)
        if not room:
            raise ObjectNotFoundException()
        if await self.db.bookings.room_is_busy(
            booking_data.room_id,
            booking_data.from_date,
            booking_data.to_date,
            hotel_id=room.hotel_id,
        ):
            raise NoFreeRoomsException()
        new_booking = booking_data.model_dump()
        new_booking["user_id"] = user_id
        new_booking["price"] = room.price
        booking = await self.db.bookings.create(BookingAddEx.model_validate(new_booking))
        await self.db.commit()
        return booking

    async def get_all(
        self,
    ) -> list[Booking]:
        assert self.db is not None
        return await self.db.bookings.get_all()

    async def get_all_for_user(
        self,
        user_id: int,
    ) -> list[Booking]:
        assert self.db is not None
        return await self.db.bookings.get_all_filtered(user_id=user_id)
