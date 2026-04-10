from sqlalchemy import select

from exceptions import ObjectNotFoundException
from .base import BaseRepository
from .mappers import UserDataMapper
from schemas.users import UserWithHashedPassword


class UserRepository(BaseRepository):
    _mapper = UserDataMapper

    async def get_user_with_password_or_none(self, **filter_by) -> UserWithHashedPassword | None:
        query = select(self._mapper.db_model).filter_by(**filter_by)
        result = await self._session.execute(query)
        obj = result.scalars().one_or_none()
        return self._mapper.to_domain_entity(obj, schema=UserWithHashedPassword) if obj else None

    async def get_user_with_password(self, **filter_by) -> UserWithHashedPassword:
        obj = await self.get_user_with_password_or_none(**filter_by)
        if obj is None:
            raise ObjectNotFoundException()
        return obj
