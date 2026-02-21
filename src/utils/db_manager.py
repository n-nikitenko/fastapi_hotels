import logging
from typing import Type

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(
            self,
            session_factory,
        hotel_repo_cls: Type,
        room_repo_cls: Type,
        user_repo_cls: Type,
    ):
        self.session_factory = session_factory
        self._committed = False
        self._rolled_back = False
        self.session = None
        self.hotel_repo_cls = hotel_repo_cls
        self.room_repo_cls = room_repo_cls
        self.user_repo_cls = user_repo_cls


    async def __aenter__(self):
        self.session = self.session_factory()
        self._committed = False
        self._rolled_back = False
        self.hotels = self.hotel_repo_cls(self.session)
        self.rooms = self.room_repo_cls(self.session)
        self.users = self.user_repo_cls(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                # При исключении автоматически откатываем
                logger.warning(
                    "Исключение в контексте транзакции, выполняется откат: %s",
                    exc_val,
                )
                await self.rollback()
            # Если исключения нет, коммит должен быть вызван явно в коде
        finally:
            # Закрываем сессию
            await self.session.close()
            logger.debug("Выход из контекста транзакции")

    async def commit(self):
        if not self.session:
            msg = "DBManager должен использоваться как асинхронный контекстный менеджер"
            raise RuntimeError(msg)

        if self._committed or self._rolled_back:
            msg = "Транзакция уже завершена"
            raise RuntimeError(msg)

        try:
            await self.session.commit()
            self._committed = True
            logger.debug("Транзакция успешно зафиксирована")
        except Exception:
            logger.exception("Ошибка при коммите транзакции")
            # При ошибке коммита автоматически откатываем
            await self.rollback()
            raise

    async def rollback(self) -> None:
        """
        Откат всех изменений в транзакции

        :raises: RuntimeError если транзакция уже завершена
        :raises: Exception если произошла ошибка при откате
        """
        if not self.session:
            msg = "DBManager должен использоваться как асинхронный контекстный менеджер"
            raise RuntimeError(msg)

        if self._committed or self._rolled_back:
            msg = "Транзакция уже завершена"
            raise RuntimeError(msg)

        try:
            await self.session.rollback()
            self._rolled_back = True
            logger.debug("Транзакция откачена")
        except Exception as e:
            logger.critical("Критическая ошибка при откате транзакции: %s", e)
            # При ошибке отката это критическая ситуация
            raise
