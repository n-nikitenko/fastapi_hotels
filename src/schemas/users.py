from typing import Annotated

from pydantic import BaseModel, Field, EmailStr


class UserRequestAdd(BaseModel):
    email: Annotated[EmailStr, Field(description="Логин пользователя")]
    password: Annotated[str, Field(description="Пароль пользователя")]

class UserAdd(BaseModel):
    email: Annotated[EmailStr, Field(description="Логин пользователя")]
    hashed_password: Annotated[str, Field(description="Пароль пользователя")]

class User(BaseModel):
    id: Annotated[int | None, Field(default=None, description="Идентификатор пользователя")]
    email: Annotated[EmailStr, Field(description="Логин пользователя")]