from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert


class BaseRepository:
    _model = None

    def __init__(self, session: AsyncSession) :
        self._session = session


    async def get_all(self, *args, **kwargs):
        query = select(self._model)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self._model).filter_by(**filter_by)

        result = await self._session.execute(query)
        return result.scalars().one_or_none()

    async def create(self, **data):
        stmt = insert(self._model).values(**data).returning(self._model)
        result = await self._session.execute(stmt)
        return result.scalars().first()


