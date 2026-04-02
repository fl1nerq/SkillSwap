import pytest
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.database import get_db, Model
from fastapi.testclient import TestClient
from src.main import app

database_url = "sqlite+aiosqlite:///:memory:"

TEST_ENGINE = create_async_engine(database_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)

Test_session_maker = async_sessionmaker(TEST_ENGINE, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
async def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
async def initialize_db(client):
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    yield

    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


async def override_get_db():
    async with Test_session_maker() as session:
        yield session


@pytest.fixture()
async def db_session():
    async with Test_session_maker() as session:
        yield session



