import json
import logging

import pytest
from pydantic import ValidationError, BaseModel

from api.dependencies import get_db_manager
from config import settings
from database import engine_null_pool, session_maker_null_pool
from main import app
from models import *
from httpx import ASGITransport, AsyncClient

from schemas import UserRequestAdd, HotelAdd, RoomAdd, RoomAddEx

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == 'TEST'

@pytest.fixture(scope="session", autouse=True)
async def init_db(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def load_mock_data(file_path: str, db_repo, schema: BaseModel):
    """
    Универсальная функция для загрузки данных из JSON в БД.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Валидируем данные через Pydantic схему перед отправкой в БД
        items_to_add = [schema(**item) for item in data]
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


@pytest.fixture(scope="session", autouse=True)
async def register_user(fill_db):
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        await ac.post(
            url="/auth/register",
            json={
                "email": "test_user@mail.ru",
                "password": "123456"
            }
        )