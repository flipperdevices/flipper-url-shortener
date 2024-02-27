from datetime import timedelta
from typing import Annotated

from app.core.dependencies import get_postgres_session
from app.core.security import create_access_token
from app.core.settings import application_settings
from app.models.url_models import URLModel
from app.schemas.auth_schemas import TokenSchema
from app.schemas.url_schemas import (
    CreateURLRequestSchema,
    ListURLResponseSchema,
    UpdateURLRequestSchema,
)
from app.services.auth_services import AuthenticationService
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.params import Path
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

router = APIRouter()


@router.post("/access-token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> TokenSchema:
    user = await AuthenticationService.authenticate_user(postgres_session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=application_settings.APP_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return TokenSchema(access_token=access_token, token_type="bearer")
