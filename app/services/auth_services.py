from typing import Annotated

from app.core.dependencies import get_postgres_session
from app.core.security import ALGORITHM, verify_password
from app.core.settings import application_settings
from app.models import UserModel
from app.schemas.auth_schemas import TokenDataSchema
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy import select
from starlette import status


class AuthenticationService:
    @staticmethod
    async def authenticate_user(postgres_session, username: str, password: str) -> UserModel | bool:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await postgres_session.execute(stmt)
        user = result.scalars().first()

        if not user:
            return False

        if not verify_password(password, user.hashed_password):
            return False

        return user
