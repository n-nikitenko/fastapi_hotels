from pydantic import BaseModel
from models.base import Base
from typing import TypeVar, Generic

SchemaType = TypeVar("SchemaType", bound=BaseModel)
DBModelType = TypeVar("DBModelType", bound=Base)


class DataMapper(Generic[SchemaType, DBModelType]):
    db_model: type[DBModelType] | None = None
    schema: type[SchemaType] | None = None

    @classmethod
    def to_domain_entity(cls, data, schema: type[SchemaType] | None = None) -> BaseModel:
        if schema is None:
            schema = cls.schema
        return schema.model_validate(data, from_attributes=True)

    @classmethod
    def from_domain_entity(
        cls,
        data: BaseModel,
        exclude_unset: bool = False,
        exclude: set[str] | None = None,
    ):
        return cls.db_model(**data.model_dump(exclude_unset=exclude_unset, exclude=exclude))
