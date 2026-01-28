from models import UserOrm
from repositories import BaseRepository
from schemas import User


class UserRepository(BaseRepository):
    _model = UserOrm
    _schema = User
