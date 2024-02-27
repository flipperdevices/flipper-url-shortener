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
from fastapi_cache import FastAPICache
from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

router = APIRouter()


@router.get("/", response_model=Page[ListURLResponseSchema], status_code=status.HTTP_200_OK)
async def get_short_urls(
    user: UserModel = Depends(get_current_user),
    postgres_session: AsyncSession = Depends(get_postgres_session),
):
    return await paginate(postgres_session, select(URLModel).order_by(URLModel.created_at))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_short_url(
    data: CreateURLRequestSchema = Body(...),
    user: UserModel = Depends(get_current_user),
    postgres_session: AsyncSession = Depends(get_postgres_session),
):
    stmt = select(URLModel).where(URLModel.domain == data.domain, URLModel.slug == data.slug)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()

    if url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The URL with this domain and slug already exists",
        )

    url_model = URLModel(
        slug=data.slug,
        domain=data.domain,
        short_url=f'https://{data.domain}/{data.slug}',
        original_url=data.original_url,
    )

    postgres_session.add(url_model)
    await postgres_session.flush()
    await postgres_session.refresh(url_model)

    return url_model


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(
    id: int = Path(...),
    user: UserModel = Depends(get_current_user),
    postgres_session: AsyncSession = Depends(get_postgres_session),
):
    stmt = select(URLModel).where(URLModel.id == id)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()
    short_url = url.short_url
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The URL with this id not found",
        )

    await postgres_session.delete(url)
    await postgres_session.flush()

    prefix = FastAPICache.get_prefix()
    await FastAPICache.clear(key=f"{prefix}:{short_url}")


@router.patch("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def patch_short_url(
    id: int = Path(...),
    data: UpdateURLRequestSchema = Body(...),
    user: UserModel = Depends(get_current_user),
    postgres_session: AsyncSession = Depends(get_postgres_session),
):
    short_url = None
    cleared_data = data.dict(exclude_unset=True)

    if not cleared_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data not provided",
        )

    stmt = select(URLModel).where(URLModel.id == id)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The URL with this id not found",
        )

    domain = cleared_data.get('domain') or url.domain
    slug = cleared_data.get('slug') or url.slug
    short_url = f'https://{domain}/{slug}'

    if data.domain or data.slug:
        stmt = select(URLModel).where(URLModel.domain == domain, URLModel.slug == slug)
        result = await postgres_session.execute(stmt)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The URL with this domain and slug already exists",
            )

        cleared_data['short_url'] = short_url

    query = update(URLModel).where(URLModel.id == id).values(**cleared_data)
    await postgres_session.execute(query)
    await postgres_session.flush()

    prefix = FastAPICache.get_prefix()
    await FastAPICache.clear(key=f"{prefix}:{short_url}")
