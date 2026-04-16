from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND


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
