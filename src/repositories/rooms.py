from models import RoomOrm
from repositories.base import BaseRepository
from schemas import Room


class RoomRepository(BaseRepository):
    _model = RoomOrm
    _schema = Room