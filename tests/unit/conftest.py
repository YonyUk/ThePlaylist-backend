from typing import Tuple
import pytest
import pytest_asyncio
import dotenv
import os
import asyncio
from httpx import AsyncClient
from asgi_lifespan import LifespanManager 
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,async_sessionmaker
from settings import ENVIRONMENT
from unittest.mock import AsyncMock
from database import BaseModel,get_database_session
from repositories import UserRepository,PlaylistRepository,TrackRepository

from main import app

dotenv.load_dotenv()

db_test_name = os.getenv('DB_TEST_NAME')
base_url:str = os.getenv('DB_BASE_URL','')
db_test_url = f'{ENVIRONMENT.DB_USER}:{ENVIRONMENT.DB_PASSWORD}@{ENVIRONMENT.DB_HOST}:{ENVIRONMENT.DB_PORT}/{db_test_name}'

DB_ENGINE = ENVIRONMENT.DB_ENGINE

@pytest.fixture(scope='session')
def event_loop():
    '''
    Docstring for event_loop

    generate the event loop for pytest_asyncio
    '''
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope='session',autouse=True)
async def test_db_engine():

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

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture
async def db_test_session(test_db_engine):
    '''
    Docstring for db_test
    
    database session for tests
    '''
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def async_client(db_test_session):
    '''
    Docstring for async_client
    
    async client for testing
    '''
    async def override_get_db():
        yield db_test_session
    
    app.dependency_overrides[get_database_session] = override_get_db

    async with LifespanManager(app):
        async with AsyncClient(base_url=base_url) as client:
            yield client
    
    app.dependency_overrides.clear()

# fixture for database:AsyncSession on unit tests of repositories
@pytest_asyncio.fixture
async def mocked_db():
    return AsyncMock(spec=AsyncSession)

@pytest_asyncio.fixture
async def mocked_get_execute_result():
    return AsyncMock(spec=Result[Tuple])

# fixture for unit tests with UserRepository already mocked
@pytest_asyncio.fixture
async def mocked_user_repository():
    return AsyncMock(spec=UserRepository)

# fixture for unit tests with TrackRepository
@pytest_asyncio.fixture
async def mocked_track_repository():
    return AsyncMock(spec=TrackRepository)