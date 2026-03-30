import json
import logging
from typing import AsyncGenerator, Any

import pytest
from pydantic import ValidationError, BaseModel

from src.api.dependencies import get_db_manager
from src.config import settings
from src.database import engine_null_pool, session_maker_null_pool
from src.main import app
from src.models import *
from httpx import ASGITransport, AsyncClient

from src.schemas import HotelAdd, RoomAddEx
from src.utils import DBManager


logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE=='TEST'


@pytest.fixture()
async def db() -> AsyncGenerator[DBManager, Any]:
    async with get_db_manager(session_factory=session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="session", autouse=True)
async def init_db(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def load_mock_data(file_path: str, db_repo, schema: type[BaseModel]):
    """
    Универсальная функция для загрузки данных из JSON в БД.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
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
        await load_mock_data('tests/mock_hotels.json', db.hotels, HotelAdd)

        # Загружаем номера
        await load_mock_data('tests/mock_rooms.json', db.rooms, RoomAddEx)

        await db.commit()


@pytest.fixture(scope="session")
async def async_client(fill_db) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(async_client):
    await async_client.post(
        url="/auth/register",
        json={
            "email": "test_user@mail.ru",
            "password": "123456"
        }
    )
