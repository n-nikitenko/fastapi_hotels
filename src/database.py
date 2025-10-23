from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings

engine = create_async_engine(url=settings.DATABASE_DSN)

session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
