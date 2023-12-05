import asyncio
from typing import Generator, Any

import asyncpg
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

import settings
from db.models import Base
from db.session import get_db
from main import app

# create async engine for interaction with database
test_engine = create_async_engine(settings.DB_TEST_URL, future=True, echo=True)

# create session for the interaction with database
test_async_session = sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

CLEAN_TABLES = [
    "users",
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def async_session_test():
    engine = create_async_engine(settings.DB_TEST_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


async def _get_test_db():
    try:
        yield test_async_session()
    finally:
        pass


@pytest.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool("postgresql://postgres_test:postgres_test@localhost:5433/postgres_test")
    yield pool
    pool.close()


@pytest.fixture
async def get_user_from_database(asyncpg_pool):
    async def get_user_from_database_by_uuid(user_id: str):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch("""SELECT * FROM users WHERE user_id = $1;""", user_id)

    return get_user_from_database_by_uuid
