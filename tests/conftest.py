from typing import Tuple
import pytest
import pytest_asyncio
import dotenv
import os
from httpx import AsyncClient,ASGITransport
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,async_sessionmaker
from settings import ENVIRONMENT
from unittest.mock import AsyncMock
from database import BaseModel,get_database_session
from repositories import UserRepository,PlaylistRepository,TrackRepository

from main import app

dotenv.load_dotenv()

db_test_name = os.getenv('DB_TEST_NAME')
base_url:str = f'{os.getenv('BASE_URL','')}{ENVIRONMENT.GLOBAL_API_PREFIX}'
db_test_url = f'{ENVIRONMENT.DB_USER}:{ENVIRONMENT.DB_PASSWORD}@{ENVIRONMENT.DB_HOST}:{ENVIRONMENT.DB_PORT}/{db_test_name}'

DB_ENGINE = ENVIRONMENT.DB_ENGINE

@pytest_asyncio.fixture
async def async_client():
    '''
    Docstring for async_client
    
    async client for testing
    '''
    # create the engine to use in the database
    engine = create_async_engine(
        url=f'{DB_ENGINE}+asyncpg://{db_test_url}',
        pool_size=ENVIRONMENT.SQLALCHEMY_POOL_SIZE,
        max_overflow=ENVIRONMENT.SQLALCHEMY_MAX_OVERFLOW,
        pool_timeout=ENVIRONMENT.SQLALCHEMY_POOL_TIMEOUT
    )

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async def override_get_db():
        async with async_session() as session:
            yield session
            await session.rollback()
    
    app.dependency_overrides[get_database_session] = override_get_db

    async with AsyncClient(base_url=base_url,transport=ASGITransport(app=app)) as client:
        yield client
    
    app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()


# fixture for database:AsyncSession on unit tests of repositories
@pytest.fixture
def mocked_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mocked_get_execute_result():
    return AsyncMock(spec=Result[Tuple])

# fixture for unit tests with UserRepository already mocked
@pytest.fixture
def mocked_user_repository():
    return AsyncMock(spec=UserRepository)

# fixture for unit tests with TrackRepository
@pytest.fixture
def mocked_track_repository():
    return AsyncMock(spec=TrackRepository)

# fixture for unit tests with PlaylistRepository
@pytest.fixture
def mocked_playlist_repository():
    return AsyncMock(spec=PlaylistRepository)