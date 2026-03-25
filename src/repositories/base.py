from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from repositories.mappers import DataMapper


class BaseRepository:
    _mapper: DataMapper

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self, *args, **kwargs):
        return await self.get_all_filtered()

    async def get_all_filtered(self, **filter_by):
        query = select(self._mapper.db_model).filter_by(**filter_by)

        result = await self._session.execute(query)
        return [self._mapper.to_domain_entity(obj) for obj in result.scalars().all()]

    async def get_one_or_none(self, **filter_by):
        query = select(self._mapper.db_model).filter_by(**filter_by)

        result = await self._session.execute(query)
        obj = result.scalars().one_or_none()
        return self._mapper.to_domain_entity(obj) if obj else None


    async def create(self, data: BaseModel):
        stmt = insert(self._mapper.db_model).values(**data.model_dump()).returning(self._mapper.db_model)
        result = await self._session.execute(stmt)
        return self._mapper.to_domain_entity(result.scalars().first())


    async def bulk_create(self, items: list[BaseModel]):
        stmt = insert(self._mapper.db_model).values([item.model_dump() for item in items])
        await self._session.execute(stmt)


    async def update(self, data: BaseModel, exclude_unset: bool = False, **filter_by):
        stmt = (
            update(self._mapper.db_model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self._mapper.db_model)
        )
        result = await self._session.execute(stmt)
        return self._mapper.to_domain_entity(result.scalars().first())


    async def delete(self, **filter_by) -> None:
        stmt = delete(self._mapper.db_model).filter_by(**filter_by)
        await self._session.execute(stmt)
