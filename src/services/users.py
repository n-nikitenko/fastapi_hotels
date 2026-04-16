from schemas import User
from schemas.users import UserWithHashedPassword
from .base import BaseService


class UsersService(BaseService):
    async def get_by_id(self, user_id: int) -> User:
        assert self.db is not None
        return await self.db.users.get_one(id=user_id)

    async def get_by_email(self, email: str) -> UserWithHashedPassword:
        assert self.db is not None
        return await self.db.users.get_user_with_password(email=email)