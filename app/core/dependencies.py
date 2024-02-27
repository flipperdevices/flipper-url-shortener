from typing import Annotated

from app.core.postgres.db import PostgresAsyncSession
from app.core.security import ALGORITHM
from app.core.settings import application_settings
from app.models import UserModel
from app.schemas.auth_schemas import TokenDataSchema
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

bearer_token = OAuth2PasswordBearer(
    tokenUrl=f"/api/{application_settings.APP_API_VERSION_STR}/auth/access-token",
    auto_error=True,
)


async def get_postgres_session() -> AsyncSession:
    async with PostgresAsyncSession() as session:
        async with session.begin():
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as exc:
                await session.rollback()
                raise Exception(f'Database error. Detail: {exc.__str__}')
            finally:
                await session.close()


async def get_current_user(
    postgres_session: AsyncSession = Depends(get_postgres_session), token: str = Depends(bearer_token)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, application_settings.APP_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenDataSchema(username=username)
    except JWTError:
        raise credentials_exception

    stmt = select(UserModel).where(UserModel.username == token_data.username)
    result = await postgres_session.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user
