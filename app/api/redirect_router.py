from app.core.cache.key_builders import short_url_key_builder
from app.core.dependencies import get_postgres_session
from app.models.url_models import URLModel
from app.tasks.url_tasks import url_visit_task
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    Header,
    HTTPException,
    Path,
)
from fastapi_cache.decorator import cache
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


@router.get("/{slug:path}", response_class=RedirectResponse)
@cache(key_builder=short_url_key_builder)
async def redirect_by_short_url(
    worker: BackgroundTasks,
    slug: str = Path(...),
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> str:
    stmt = select(URLModel).where(URLModel.slug == slug)
    result = await postgres_session.execute(stmt)
    url = result.scalars().first()

    if url:
        worker.add_task(url_visit_task, slug=slug)
        return url.original_url

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The URL not found",
    )
