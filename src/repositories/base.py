import logging
from typing import cast

import asyncpg
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, CursorResult

from exceptions import ObjectNotFoundException, ObjectAlreadyExist
from repositories.mappers import DataMapper

logger = logging.getLogger(__name__)

class BaseRepository:
    _mapper: type[DataMapper]

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

    async def get_one(self, **filter_by):
        obj = await self.get_one_or_none(**filter_by)
        if obj is None:
            raise ObjectNotFoundException
        return obj

    async def create(self, data: BaseModel):
        stmt = (
            insert(self._mapper.db_model)
            .values(**data.model_dump())
            .returning(self._mapper.db_model)
        )
        try:
            result = await self._session.execute(stmt)
        except IntegrityError as exc:
            orig_cause = getattr(exc.orig, "__cause__", None)
            logger.error("Не удалось добавить данные в БД: data=", data)
            if isinstance(orig_cause, asyncpg.exceptions.UniqueViolationError):
                raise ObjectAlreadyExist() from exc
            raise

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
        obj = result.scalars().first()
        if obj is None:
            raise ObjectNotFoundException()
        return self._mapper.to_domain_entity(obj)

    async def delete(self, **filter_by) -> None:
        stmt = delete(self._mapper.db_model).filter_by(**filter_by)
        result: CursorResult = cast(CursorResult, await self._session.execute(stmt))
        if result.rowcount == 0:
            raise ObjectNotFoundException()
