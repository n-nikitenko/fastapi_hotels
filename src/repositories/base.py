from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete


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

    async def create(self, data: BaseModel):
        stmt = insert(self._model).values(**data.model_dump()).returning(self._model)
        result = await self._session.execute(stmt)
        return result.scalars().first()


    async def update(self, data: BaseModel, exclude_unset : bool = False, **filter_by):
        stmt = (
            update(self._model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self._model)
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()


    async def delete(self, **filter_by) -> None:
        stmt = delete(self._model).filter_by(**filter_by)
        result = await self._session.execute(stmt)


