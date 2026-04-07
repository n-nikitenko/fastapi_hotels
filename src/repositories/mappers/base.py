from pydantic import BaseModel
from models.base import Base
from typing import TypeVar, Generic, ClassVar, cast

SchemaType = TypeVar("SchemaType", bound=BaseModel)
DBModelType = TypeVar("DBModelType", bound=Base)


class DataMapper(Generic[SchemaType, DBModelType]):
    db_model: ClassVar[type]  # конкретный тип задаётся в подклассе
    schema: ClassVar[type[BaseModel]]

    @classmethod
    def to_domain_entity(
        cls,
        data: object,
        schema: type[SchemaType] | None = None,
    ) -> SchemaType:
        target = schema or cls.schema
        return cast(SchemaType, target.model_validate(data, from_attributes=True))

    @classmethod
    def from_domain_entity(
        cls,
        data: BaseModel,
        exclude_unset: bool = False,
        exclude: set[str] | None = None,
    ) -> DBModelType:
        return cast(
            DBModelType,
            cls.db_model(
                **data.model_dump(
                    exclude_unset=exclude_unset,
                    exclude=exclude,
                )
            ),
        )
