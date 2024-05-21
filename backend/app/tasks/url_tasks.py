from datetime import datetime

from app.core.postgres.db import PostgresAsyncSession
from app.models import URLModel
from sqlalchemy import select


async def url_visit_task(slug: str):
    async with PostgresAsyncSession() as postgres_session:
        async with postgres_session.begin():
            stmt = select(URLModel).where(URLModel.slug == slug).with_for_update()
            result = await postgres_session.execute(stmt)
            url = result.scalars().first()

            if not url:
                return

            date = datetime.utcnow()
            url.visits = url.visits + 1
            url.last_visit_at = date
            url.updated_at = date

            await postgres_session.flush()