import pytest

from database import engine_null_pool
from models import *

@pytest.fixture(autouse=True)
async def init_db():
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)