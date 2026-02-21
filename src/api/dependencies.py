from typing import Annotated

from fastapi import Depends, Request, HTTPException
from fastapi.params import Query
from jwt import DecodeError
from pydantic import BaseModel, Field

from services import AuthService
from utils import DBManager
from database import session_maker
from repositories import HotelRepository, RoomRepository, UserRepository

class PaginationParams(BaseModel):
    page: Annotated[int | None, Field(), Query(1, ge=1, description="Номер страницы")]
    limit: Annotated[int | None, Query(None, ge=1, lt=30, description="Кол-во отелей на странице")]


PaginationDep = Annotated[PaginationParams, Depends()]

def get_access_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if access_token:
        return access_token
    raise HTTPException(status_code=401, detail="Необходима авторизация")

def get_user_id(access_token: Annotated[str, Depends(get_access_token)])-> int:
    try:
        data = AuthService.decode_token(access_token)
        return data["user_id"]
    except DecodeError:
        raise HTTPException(status_code=401, detail="Неверный токен доступа")

UserIdDep = Annotated[int, Depends(get_user_id)]

def get_db_manager() -> DBManager:
    return DBManager(
        session_maker,
        hotel_repo_cls=HotelRepository,
        user_repo_cls=UserRepository,
        room_repo_cls=RoomRepository,
    )

async def get_db():
    async with get_db_manager() as db:
        yield db

DbDep = Annotated[DBManager, Depends(get_db)]