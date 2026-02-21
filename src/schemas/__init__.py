from .hotels import HotelAdd, HotelPatch, Hotel
from .rooms import Room, RoomAdd, RoomPatch, RoomAddEx
from .users import UserAdd, UserRequestAdd, User
from .bookings import BookingAdd, BookingAddEx, Booking

__all__ = ["HotelAdd", "HotelPatch", "Hotel", "Room", "RoomAdd", "RoomAddEx", "RoomPatch", "UserAdd", "UserRequestAdd",
           "User", "BookingAdd", "BookingAddEx", "Booking"]
