from datetime import timedelta, timezone, datetime

import jwt
from fastapi import APIRouter, HTTPException, Response, Request

from config import settings
from database import session_maker
from repositories import UserRepository
from schemas import UserRequestAdd, UserAdd, User
from pwdlib import PasswordHash

from services import AuthService

router = APIRouter(prefix="/auth", tags = ["Аутентификация и авторизация"])

@router.post("/register", summary="Регистрация")
async def register_user(data: UserRequestAdd):
    async with session_maker() as session:
        repo = UserRepository(session)
        hashed_password = AuthService().get_password_hash(data.password)

        base = data.model_dump(exclude={"password"})
        processed_data = UserAdd(**base, hashed_password=hashed_password)
        await repo.create(processed_data)
        await session.commit()

    return {"ok": True}


@router.post("/login", summary="Вход")
async def login_user(data: UserRequestAdd, response: Response):
    async with session_maker() as session:
        repo = UserRepository(session)
        user = await repo.get_user_with_password_or_none(email=data.email)
        if not user or not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверные email или пароль")
        access_token = AuthService.create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)

    return {"access_token": access_token}


@router.get("/only_auth")
def only_auth(request: Request):
    access_token = request.cookies.get("access_token")
    return {"access_token": access_token}