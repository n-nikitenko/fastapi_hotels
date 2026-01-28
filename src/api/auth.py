from fastapi import APIRouter

from database import session_maker
from repositories import UserRepository
from schemas import UserRequestAdd, UserAdd
from pwdlib import PasswordHash

router = APIRouter(prefix="/auth", tags = ["Аутентификация и авторизация"])
password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)

@router.post("/register", summary="Регистрация")
async def register_user(data: UserRequestAdd):
    async with session_maker() as session:
        repo = UserRepository(session)
        hashed_password = get_password_hash(data.password)

        base = data.model_dump(exclude={"password"})
        processed_data = UserAdd(**base, hashed_password=hashed_password)
        await repo.create(processed_data)
        await session.commit()

    return {"ok": True}

