from app.core.settings import application_settings
from app.core.cache.decorators import cache_visits
from app.core.cache.key_builders import short_url_key_builder
from app.core.dependencies import get_postgres_session
from app.models.url_models import UrlModel
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    Header,
    HTTPException,
    Path,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse

router = APIRouter(
    # Hide this router from the OpenAPI docs since it's not a part of
    # the API, but rather a part of the main app.
    include_in_schema=False,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Short URL not found",
        },
        status.HTTP_307_TEMPORARY_REDIRECT: {
            "description": "Successfully redirected to the original URL",
        },
    },
)


@router.get("/", response_class=RedirectResponse)
async def redirect_root() -> str:
    root_url = application_settings.ROOT_REDIRECT_URL

    if root_url:
        return root_url

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The URL not found",
    )


@router.get("/{slug:path}", response_class=RedirectResponse)
@cache_visits(key_builder=short_url_key_builder)
async def redirect_by_short_url(
    slug: str = Path(..., min_length=1),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> str:
    stmt = select(UrlModel).where(UrlModel.slug == slug)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()

    if url:
        return url.original_url

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The URL not found",
    )
