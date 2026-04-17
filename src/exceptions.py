from fastapi import HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
)


class BaseHotelsException(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(BaseHotelsException):
    detail = "Объект не найден"


class ObjectAlreadyExist(BaseHotelsException):
    detail = "Объект уже существует"


class NoFreeRoomsException(BaseHotelsException):
    detail = "Нет свободных номеров"


class InvalidTokenException(BaseHotelsException):
    detail = "Неверный токен доступа"

class HotelsBaseHTTPException(HTTPException):
    status_code = HTTP_404_NOT_FOUND
    detail = "Неожиданная ошибка"

    def __init__(self, status_code: int | None = None, detail: str | None = None, *args, **kwargs):
        super().__init__(
            status_code=status_code or self.status_code,
            detail=detail or self.detail,
            *args,
            **kwargs,
        )


class HotelNotFoundHttpException(HotelsBaseHTTPException):
    status_code = HTTP_404_NOT_FOUND
    detail = "Отель не найден"


class RoomNotFoundHttpException(HotelsBaseHTTPException):
    status_code = HTTP_404_NOT_FOUND
    detail = "Номер не найден"


class RoomIsBusyHttpException(HotelsBaseHTTPException):
    status_code = (HTTP_409_CONFLICT,)
    detail = "Номер уже забронирован"


class DatesInconsistencyHttpException(HotelsBaseHTTPException):
    status_code = (HTTP_422_UNPROCESSABLE_CONTENT,)
    detail = "Дата выезда не может быть раньше даты заезда"


class NoImageFileHttpException(HotelsBaseHTTPException):
    status_code = HTTP_422_UNPROCESSABLE_CONTENT
    detail = "Имя файла не указано"


class UnauthorizedHttpException(HotelsBaseHTTPException):
    status_code = HTTP_401_UNAUTHORIZED
    detail = "Необходима авторизация"


class InvalidTokenHttpException(HotelsBaseHTTPException):
    status_code = HTTP_401_UNAUTHORIZED
    detail = "Неверный токен доступа"


class IncorrectEmailOrPasswordHttpException(HotelsBaseHTTPException):
    status_code = HTTP_401_UNAUTHORIZED
    detail = "Неверные email или пароль"


class UserAlreadyExistHttpException(HotelsBaseHTTPException):
    status_code = HTTP_409_CONFLICT
    detail = "Пользователь с указанным email уже зарегистрирован"
