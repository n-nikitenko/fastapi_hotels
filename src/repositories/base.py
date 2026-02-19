from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete


class BaseRepository:
    _model = None
    _schema: BaseModel = None

    def _to_schema(self, orm_obj, schema: BaseModel | None = None):
        if schema is None:
            schema = self._schema
        return schema.model_validate(orm_obj, from_attributes=True) # todo: убрать связь с Pydantic


    def __init__(self, session: AsyncSession) :
        self._session = session


    async def get_all(self, *args, **kwargs):
        return await self.get_all_filtered()

    async def get_all_filtered(self, **filter_by):
        query = select(self._model).filter_by(**filter_by)

        result = await self._session.execute(query)
        return [self._to_schema(obj, self._schema) for obj in result.scalars().all()]

    async def get_one_or_none(self, **filter_by):
        query = select(self._model).filter_by(**filter_by)

        result = await self._session.execute(query)
        obj = result.scalars().one_or_none()
        return self._to_schema(obj, self._schema)  if obj else None

    async def create(self, data: BaseModel):
        stmt = insert(self._model).values(**data.model_dump()).returning(self._model)
        result = await self._session.execute(stmt)
        return self._to_schema(result.scalars().first(), self._schema)


    async def update(self, data: BaseModel, exclude_unset : bool = False, **filter_by):
        stmt = (
            update(self._model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self._model)
        )
        result = await self._session.execute(stmt)
        return self._to_schema(result.scalars().first(), self._schema)


    async def delete(self, **filter_by) -> None:
        stmt = delete(self._model).filter_by(**filter_by)
        await self._session.execute(stmt)


