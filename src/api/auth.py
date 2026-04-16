from fastapi import APIRouter, HTTPException, Response
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT

from api.dependencies import UserIdDep, DbDep
from exceptions import ObjectNotFoundException, ObjectAlreadyExist
from schemas import UserRequestAdd, UserAdd, User

from services import AuthService, UsersService

router = APIRouter(prefix="/auth", tags=["Аутентификация и авторизация"])


def _raise_401():
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Неверные email или пароль")


@router.post("/register", summary="Регистрация")
async def register_user(
    data: UserRequestAdd,
    db: DbDep,
):
    hashed_password = AuthService().get_password_hash(data.password)

    base = data.model_dump(exclude={"password"})
    processed_data = UserAdd(**base, hashed_password=hashed_password)
    try:
        await db.users.create(processed_data)
    except ObjectAlreadyExist:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Пользователь с указанным email уже зарегистрирован",
        )

    await db.commit()

    return {"ok": True}


@router.post("/login", summary="Вход")
async def login_user(
    data: UserRequestAdd,
    response: Response,
    db: DbDep,
):
    try:
        user = await UsersService(db).get_by_email(email=data.email)
    except ObjectNotFoundException:
        _raise_401()
    else:
        if not AuthService().verify_password(data.password, user.hashed_password):
            _raise_401()
        access_token = AuthService.create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)

        return {"access_token": access_token}


@router.post("/logout", summary="Выход")
async def logout_user(
    user_id: UserIdDep,
    response: Response,
    db: DbDep,
):
    await UsersService(db).get_by_id(user_id=user_id)
    response.delete_cookie("access_token")
    return {"ok": True}


@router.get("/me")
async def get_me(
    user_id: UserIdDep,
    db: DbDep,
) -> User:
    return await UsersService(db).get_by_id(user_id=user_id)
