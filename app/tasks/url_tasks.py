from datetime import datetime

from app.core.postgres.db import PostgresAsyncSession
from app.models import URLModel
from sqlalchemy import select, update


async def url_visit_task(slug: str):
    async with PostgresAsyncSession() as postgres_session:
        async with postgres_session.begin():
            date = datetime.utcnow()

            update_values = {'visits': URLModel.visits + 1, 'last_visit_at': date, 'updated_at': date}
            query = update(URLModel).where(URLModel.slug == slug).values(**update_values)
            await postgres_session.execute(query)
            await postgres_session.flush()
