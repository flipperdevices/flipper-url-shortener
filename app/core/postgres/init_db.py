from app.core.postgres.db import PostgresAsyncSession
from app.core.security import get_password_hash
from app.core.settings import application_settings
from app.models.user_models import UserModel
from sqlalchemy import select


async def init() -> None:
    async with PostgresAsyncSession() as postgres_session:
        async with postgres_session.begin():
            stmt = select(UserModel).where(UserModel.username == application_settings.FIRST_USER_USERNAME)
            result = await postgres_session.execute(stmt)
            if not result.scalars().first():
                user_model = UserModel(
                    username=application_settings.FIRST_USER_USERNAME,
                    email=application_settings.FIRST_USER_EMAIL,
                    hashed_password=get_password_hash(application_settings.FIRST_USER_PASSWORD),
                    is_superuser=True,
                )
                postgres_session.add(user_model)
                await postgres_session.flush()
                await postgres_session.refresh(user_model)
