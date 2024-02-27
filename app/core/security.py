import secrets
from datetime import datetime, timedelta, timezone
from hashlib import md5
from typing import Any, Optional, Union

from app.core.settings import application_settings
from jose import jwt
from loguru import logger
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Algorithm used to generate the JWT token
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=application_settings.APP_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, application_settings.APP_SECRET_KEY, algorithm=ALGORITHM)


def create_api_key() -> str:
    return md5(secrets.token_bytes(32)).hexdigest()
