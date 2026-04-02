from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

engine = create_async_engine(settings.DATABASE_URL_asyncpg, echo=True)

new_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with new_session() as session:
        yield session

class Model(DeclarativeBase):
    pass