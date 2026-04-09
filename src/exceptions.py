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