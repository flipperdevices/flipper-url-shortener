from app.core.postgres.db import PostgresAsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_postgres_session() -> AsyncSession:
    async with PostgresAsyncSession() as session:
        async with session.begin():
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as exc:
                await session.rollback()
                raise Exception(f"Database error. Detail: {exc.__str__}")
            finally:
                await session.close()
