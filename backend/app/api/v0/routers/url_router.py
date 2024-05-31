from typing import Literal

from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page
from sqlalchemy.orm import selectinload
from fastapi.params import Path
from fastapi_cache import FastAPICache
from sqlalchemy import update, select, delete, and_
from starlette import status
from fastapi import HTTPException, APIRouter, Depends, Query, Body

from app.schemas.url_schemas import (
    CreateUrlResponseSchema,
    UpdateUrlRequestSchema,
    CreateUrlRequestSchema,
    AddTagUrlRequestSchema,
    ListUrlResponseSchema,
)
from app.models.url_models import UrlTagModel, UrlModel
from app.models.tag_models import TagModel
from app.core.dependencies import get_postgres_session

router = APIRouter()


@router.get(
    "/", response_model=Page[ListUrlResponseSchema], status_code=status.HTTP_200_OK
)
async def get_short_urls(
    sort_by: Literal[
        "updated_at", "created_at", "slug", "original_url", "visits", "last_visit_at"
    ] = Query("created_at", description="Which element to sort by"),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
    tag_ids: list[int] = Query(None),
    postgres_session: AsyncSession = Depends(get_postgres_session),
):
    order_stmt = getattr(getattr(UrlModel, sort_by, "created_at"), sort_order, "desc")
    select_stmt = select(UrlModel).options(selectinload(UrlModel.tags))

    if tag_ids:
        select_stmt = select_stmt.where(
            UrlModel.tags.any(UrlTagModel.tag_id.in_(tag_ids))
        )

    return await paginate(postgres_session, select_stmt.order_by(order_stmt()))


@router.post(
    "/", response_model=CreateUrlResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_short_url(
    data: CreateUrlRequestSchema = Body(...),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> UrlModel:
    stmt = select(UrlModel).where(UrlModel.slug == data.slug)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()

    if url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The URL with this slug already exists",
        )

    url_model = UrlModel(
        slug=data.slug,
        original_url=data.original_url,
    )

    postgres_session.add(url_model)
    await postgres_session.flush()
    await postgres_session.refresh(url_model)

    return url_model


@router.post("/{id}/tag", response_model=list[int], status_code=status.HTTP_201_CREATED)
async def add_tag_url(
    id: int = Path(...),
    data: AddTagUrlRequestSchema = Body(...),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> list[int]:
    stmt = select(UrlModel).where(UrlModel.id == id)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The URL with this id not found",
        )

    url_tags = []
    for tag_id in data.tag_ids:
        stmt = select(TagModel).where(TagModel.id == tag_id)
        result = await postgres_session.execute(stmt)
        tag = result.scalars().first()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The Tag with id: {tag_id} not found",
            )

        stmt = select(UrlTagModel).where(
            and_(UrlTagModel.url_id == id, UrlTagModel.tag_id == tag_id)
        )
        result = await postgres_session.execute(stmt)
        url_tag = result.scalars().first()

        if url_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The Tag with id: {tag_id} already added to the url",
            )

        url_tags.append(UrlTagModel(url_id=id, tag_id=tag_id))

    postgres_session.add_all(url_tags)
    await postgres_session.flush()

    return data.tag_ids


@router.delete("/{id}/tag", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag_url(
    id: int = Path(...),
    data: AddTagUrlRequestSchema = Body(...),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> None:
    stmt = select(UrlModel).where(UrlModel.id == id)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The URL with this id not found",
        )

    url_tags = []
    for tag_id in data.tag_ids:
        stmt = select(TagModel).where(TagModel.id == tag_id)
        result = await postgres_session.execute(stmt)
        tag = result.scalars().first()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The Tag with id: {tag_id} not found",
            )

        stmt = select(UrlTagModel).where(
            and_(UrlTagModel.url_id == id, UrlTagModel.tag_id == tag_id)
        )
        result = await postgres_session.execute(stmt)
        url_tag = result.scalars().first()

        if not url_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The Tag with id: {tag_id} not added to the url",
            )

        url_tags.append(url_tag.tag_id)

    query = delete(UrlTagModel).where(
        and_(UrlTagModel.url_id == id, UrlTagModel.tag_id.in_(url_tags))
    )
    await postgres_session.execute(query)
    await postgres_session.flush()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(
    id: int = Path(...),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> None:
    stmt = select(UrlModel).where(UrlModel.id == id)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The URL with this id not found",
        )

    slug = url.slug

    await postgres_session.delete(url)
    await postgres_session.flush()

    prefix = FastAPICache.get_prefix()
    await FastAPICache.clear(key=f"{prefix}:{slug}")


@router.patch("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def patch_short_url(
    id: int = Path(...),
    data: UpdateUrlRequestSchema = Body(...),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> None:
    cleared_data = data.dict(exclude_unset=True)

    if not cleared_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data not provided",
        )

    stmt = select(UrlModel).where(UrlModel.id == id)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The URL with this id not found",
        )

    slug = cleared_data.get("slug") or url.slug

    if data.slug:
        stmt = select(UrlModel).where(UrlModel.slug == slug)
        result = await postgres_session.execute(stmt)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The URL with this domain and slug already exists",
            )

    query = update(UrlModel).where(UrlModel.id == id).values(**cleared_data)
    await postgres_session.execute(query)
    await postgres_session.flush()

    prefix = FastAPICache.get_prefix()
    await FastAPICache.clear(key=f"{prefix}:{slug}")
