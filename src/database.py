from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings

engine = create_async_engine(url=settings.DATABASE_DSN, echo=True)

engine_null_pool = create_async_engine(url=settings.DATABASE_DSN, poolclass=NullPool)

session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
session_maker_null_pool  = async_sessionmaker(bind=engine_null_pool, expire_on_commit=False)
