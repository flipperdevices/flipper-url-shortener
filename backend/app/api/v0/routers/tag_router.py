from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page
from fastapi.params import Query, Path
from sqlalchemy import update, select
from starlette import status
from fastapi import HTTPException, APIRouter, Depends, Body

from app.schemas.tag_schemas import (
    CreateTagResponseSchema,
    UpdateTagRequestSchema,
    CreateTagRequestSchema,
    ListTagResponseSchema,
)
from app.models.tag_models import TagModel
from app.core.dependencies import get_postgres_session

router = APIRouter()


@router.get(
    "/", response_model=Page[ListTagResponseSchema], status_code=status.HTTP_200_OK
)
async def get_tags(
    query: str = Query(None, min_length=1, max_length=150),
    postgres_session: AsyncSession = Depends(get_postgres_session),
):
    select_stmt = select(TagModel)
    if query:
        select_stmt = select_stmt.where(TagModel.name.ilike(f"%{query}%"))

    return await paginate(postgres_session, select_stmt.order_by(TagModel.created_at))


@router.post(
    "/", response_model=CreateTagResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_tag_url(
    data: CreateTagRequestSchema = Body(...),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> TagModel:
    stmt = select(TagModel).where(TagModel.name == data.name)
    result = await postgres_session.execute(stmt)
    tag = result.scalars().first()

    if tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Tag with this name already exists",
        )

    tag_model = TagModel(name=data.name)

    postgres_session.add(tag_model)
    await postgres_session.flush()
    await postgres_session.refresh(tag_model)

    return tag_model


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    id: int = Path(...),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> None:
    stmt = select(TagModel).where(TagModel.id == id)
    result = await postgres_session.execute(stmt)
    tag = result.scalars().first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The Tag with this id not found",
        )

    await postgres_session.delete(tag)
    await postgres_session.flush()


@router.patch("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def patch_tag(
    id: int = Path(...),
    data: UpdateTagRequestSchema = Body(...),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> None:
    cleared_data = data.dict(exclude_unset=True)

    if not cleared_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data not provided",
        )

    stmt = select(TagModel).where(TagModel.id == id)
    result = await postgres_session.execute(stmt)
    tag = result.scalars().first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The Tag with this id not found",
        )

    stmt = select(TagModel).where(TagModel.name == data.name)
    result = await postgres_session.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The Tag with this name already exists",
        )

    query = update(TagModel).where(TagModel.id == id).values(**cleared_data)
    await postgres_session.execute(query)
    await postgres_session.flush()
