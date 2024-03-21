from contextlib import asynccontextmanager

from fastapi_cache.backends.inmemory import InMemoryBackend

from app.api import router as api_router
from app.api.redirect_router import router as redirect_router
from app.core.settings import application_settings
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_pagination import add_pagination


@asynccontextmanager
async def lifespan(application: FastAPI):
    FastAPICache.init(
        backend=InMemoryBackend(),
        prefix="fastapi-cache",
        expire=application_settings.CACHE_EXPIRE_TIME,
        enable=application_settings.CACHE_ACTIVE,
    )
    yield


app = FastAPI(
    title=application_settings.APP_TITLE,
    debug=application_settings.APP_DEBUG,
    version=application_settings.APP_VERSION,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    lifespan=lifespan,
)


app.include_router(api_router)
app.include_router(redirect_router)

add_pagination(app)
