import mimetypes
import time
from typing import Tuple
import magic
import pytest
from _pytest.logging import LogCaptureFixture
import logging
import pytest_asyncio
import dotenv
import os
from httpx import AsyncClient,ASGITransport
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,async_sessionmaker
from settings import ENVIRONMENT
from unittest.mock import AsyncMock, MagicMock
from database import BaseModel,get_database_session
from repositories import UserRepository,PlaylistRepository,TrackRepository
from services import get_backblazeb2_service,BackBlazeB2Service
from unittest.mock import AsyncMock
from b2sdk.v2 import FileVersion

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
    # adds a mime type for .m4a extension file
    mimetypes.add_type("audio/x-m4a",'.m4a')

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

    filepath = os.path.join(os.getcwd(),os.path.join('tests',os.path.join('tests_assets','Awaken.m4a')))
    file_size = os.stat(filepath).st_size
    content_type,_ = mimetypes.guess_type(filepath)

    async def override_get_db():
        async with async_session() as session:
            yield session
            await session.rollback()
    
    def mock_upload(*args,**kwargs):
        result = AsyncMock(spec=FileVersion)
        result.configure_mock(
            id_='file_id',
            file_name=kwargs['file_name'],
            content_type=kwargs['content_type'],
            content_sha1='sha1',
            size=file_size,
            upload_timestamp=time.time()
        )
        return result
    
    def mock_copy(*args,**kwargs):
        result = AsyncMock(spec=FileVersion)
        result.configure_mock(
            id_=kwargs['file_id'],
            file_name=kwargs['new_file_name'],
            content_type=content_type,
            content_sha1='sha1',
            size=file_size,
            upload_timestamp=time.time()
        )
        return result
    
    async def override_get_backblazeb2_service():
        service = BackBlazeB2Service(True)
        service._bucket = MagicMock()
        service._api = MagicMock()
        service._bucket.upload.side_effect = mock_upload
        service._bucket.copy.side_effect = mock_copy
        try:
            yield service
        finally:
            service = None
    
    app.dependency_overrides[get_database_session] = override_get_db
    app.dependency_overrides[get_backblazeb2_service] = override_get_backblazeb2_service

    async with AsyncClient(base_url=base_url,transport=ASGITransport(app=app)) as client:
        yield client
    
    app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    await engine.dispose()

# fixture to save the faileds tests into a file
@pytest.hookimpl(tryfirst=True,hookwrapper=True)
def pytest_runtest_makereport(item,call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call':
        setattr(item,'rep_call',report)

@pytest.fixture(autouse=True)
def log_on_failure(request,caplog:LogCaptureFixture):
    caplog.set_level(logging.DEBUG)
    yield

    if hasattr(request.node,'rep_call'):
        report = request.node.rep_call
        if report.failed:
            log_text = report.longreprtext
            test_name = request.node.name
            filename = f'logs_failed_{test_name}.log'
            with open(filename,'a',encoding='utf-8') as f:
                f.write(f"========== Test's logs failed: {test_name} ==========\n")
                f.write(log_text)
                f.write('\n\n')

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