from models import RoomOrm
from repositories.base import BaseRepository


class RoomRepository(BaseRepository):
    _model = RoomOrm