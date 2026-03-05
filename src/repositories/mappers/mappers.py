from models import HotelOrm, RoomOrm, UserOrm, FacilityOrm, RoomFacilityOrm, BookingOrm
from schemas import Hotel, Room, User, Facility, RoomFacility, Booking
from .base import DataMapper


class HotelDataMapper(DataMapper[Hotel, HotelOrm]):
    db_model = HotelOrm
    schema = Hotel

class RoomDataMapper(DataMapper[Room, RoomOrm]):
    db_model = RoomOrm
    schema = Room

class UserDataMapper(DataMapper[User, UserOrm]):
    db_model = UserOrm
    schema = User

class FacilityDataMapper(DataMapper[Facility, FacilityOrm]):
    db_model = FacilityOrm
    schema = Facility

class RoomsFacilitiesDataMapper(DataMapper[RoomFacility, RoomFacilityOrm]):
    db_model = RoomFacilityOrm
    schema = RoomFacility

class BookingDataMapper(DataMapper[Booking, BookingOrm]):
    db_model = BookingOrm
    schema = Booking