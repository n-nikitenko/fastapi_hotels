import json
import logging
from typing import AsyncGenerator, Any, Tuple, Optional

import pytest
from fastapi_cache import FastAPICache, Backend
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError, BaseModel
from starlette.status import HTTP_200_OK

import tasks
from database import session_maker_null_pool, engine_null_pool
from src.api.dependencies import get_db_manager, get_db
from src.config import settings
from src.main import app
from src.models import *  # noqa: F403
from src.schemas import HotelAdd, RoomAddEx
from src.utils import DBManager


logger = logging.getLogger(__name__)
TEST_USER_EMAIL = "test_user@mail.ru"
TEST_USER_PASSWORD = "123456"


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session")
def test_user_credentials() -> dict[str, str]:
    return {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }


class NoOpBackend(Backend):
    """Backend-заглушка для тестов, который ничего не кэширует"""

    async def get_with_ttl(self, key: str) -> Tuple[int, Optional[bytes]]:
        return 0, None

    async def get(self, key):
        return None

    async def set(self, key, value, expire=None):
        pass

    async def clear(self, namespace=None, key=None):
        pass


@pytest.fixture(scope="session", autouse=True)
def disable_cache():
    """Отключает кэширование по умолчанию для воспроизводимости тестов"""
    FastAPICache.init(NoOpBackend(), prefix="test-cache")


@pytest.fixture(autouse=True)
def disable_celery_tasks(monkeypatch):
    """
    Отключает отправку celery-задач в брокер во время тестов.
    """
    monkeypatch.setattr(tasks.test_task, "delay", lambda *args, **kwargs: None)
    monkeypatch.setattr(tasks.resize_image, "delay", lambda *args, **kwargs: None)


@pytest.fixture(scope="session")
def enable_cache():
    """
    Опциональная фикстура для тестов, которым нужно проверить кэширование.

    Использование:
        async def test_with_cache(async_client, enable_cache):
            # Кэширование работает с InMemoryBackend
            response = await async_client.get("/facilities/")
    """
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")


@pytest.fixture(scope="session", autouse=True)
async def init_db(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture()
async def db() -> AsyncGenerator[DBManager, Any]:
    async with get_db_manager(session_factory=session_maker_null_pool) as db:
        yield db


async def load_mock_data(file_path: str, db_repo, schema: type[BaseModel]):
    """
    Универсальная функция для загрузки данных из JSON в БД.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Валидируем данные через Pydantic схему перед отправкой в БД
        items_to_add = [schema.model_validate(item) for item in data]
        await db_repo.bulk_create(items_to_add)

    except FileNotFoundError:
        logger.error(f"Файл не найден: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Ошибка парсинга JSON в файле: {file_path}")
        raise
    except ValidationError as e:
        logger.error(f"Данные в JSON не соответствуют схеме {schema.__name__}: {e}")
        raise
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при загрузке {file_path}: {e}")
        raise


@pytest.fixture(scope="session", autouse=True)
async def fill_db(init_db):
    async with get_db_manager(session_factory=session_maker_null_pool) as db:
        # Загружаем отели
        await load_mock_data("tests/mock_hotels.json", db.hotels, HotelAdd)

        # Загружаем номера
        await load_mock_data("tests/mock_rooms.json", db.rooms, RoomAddEx)

        await db.commit()


@pytest.fixture(scope="session")
async def async_client(fill_db) -> AsyncGenerator[AsyncClient, Any]:
    async def _override_get_db():
        async with get_db_manager(session_factory=session_maker_null_pool) as db:
            yield db

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
async def register_user(async_client, test_user_credentials):
    await async_client.post(
        url="/auth/register",
        json=test_user_credentials,
    )


@pytest.fixture(scope="session")
async def auth_async_client(async_client, register_user, test_user_credentials) -> AsyncClient:
    """
    Клиент с установленной auth-cookie.
    Используйте в тестах, где нужен авторизованный пользователь.
    """
    response = await async_client.post(
        url="/auth/login",
        json=test_user_credentials,
    )
    assert response.status_code == HTTP_200_OK
    access_token_from_body = response.json().get("access_token")
    access_token_from_cookie = async_client.cookies.get("access_token")
    assert access_token_from_body, "В ответе логина отсутствует access_token"
    assert access_token_from_cookie, "После логина не установился access_token cookie"
    assert access_token_from_cookie == access_token_from_body, (
        "Токен в cookie не совпадает с токеном в response body"
    )
    return async_client
