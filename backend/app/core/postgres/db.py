from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.settings import application_settings

postgres_async_engine = create_async_engine(
    url=application_settings.POSTGRES_URL,
    pool_size=30,
    pool_recycle=1800,
    max_overflow=0,
    echo=False,
)

PostgresAsyncSession = async_sessionmaker(postgres_async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
