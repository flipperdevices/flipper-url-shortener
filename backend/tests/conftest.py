import asyncio

import pytest
from fastapi_cache.backends.inmemory import InMemoryBackend
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi_cache import FastAPICache
from httpx import ASGITransport, AsyncClient

from app.models.url_models import BaseModel
from app.core.dependencies import get_postgres_session
from app.main import app as application
from app.core import settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def engine():
    engine = create_async_engine(settings.application_settings.POSTGRES_URL)
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    async with engine.connect() as conn:
        await conn.begin()
        async_session = sessionmaker(conn, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            yield session
        await conn.rollback()


@pytest.fixture
def app(session):
    application.dependency_overrides[get_postgres_session] = lambda: session
    return application


@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True, scope="session")
def setup_cache():
    FastAPICache.init(InMemoryBackend(), prefix="test-cache")
