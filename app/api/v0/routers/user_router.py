from datetime import timedelta

from app.core.dependencies import get_current_user, get_postgres_session
from app.models import UserModel
from app.models.url_models import URLModel
from app.schemas.url_schemas import (
    CreateURLRequestSchema,
    ListURLResponseSchema,
    UpdateURLRequestSchema,
)
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.params import Path
from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_current_user(
    user: UserModel = Depends(get_current_user),
):
    return user
