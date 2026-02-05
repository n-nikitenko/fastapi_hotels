from sqlalchemy import select

from models import UserOrm
from repositories import BaseRepository
from schemas import User
from schemas.users import UserWithHashedPassword


class UserRepository(BaseRepository):
    _model = UserOrm
    _schema = User

    async def get_user_with_password_or_none(self, **filter_by) -> UserWithHashedPassword | None:
        query = select(self._model).filter_by(**filter_by)
        result = await self._session.execute(query)
        obj = result.scalars().one_or_none()
        return self._to_schema(obj, UserWithHashedPassword) if obj else None
