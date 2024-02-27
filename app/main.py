from contextlib import asynccontextmanager

from aiomcache import Client
from app.api import router as api_router
from app.api.redirect_router import router as redirect_router
from app.core.cache.backends import CustomMemcachedBackend
from app.core.postgres import init_db
from app.core.settings import application_settings
from fastapi import FastAPI, Request, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi_cache import FastAPICache
from fastapi_pagination import add_pagination
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa
    memcached = Client(application_settings.MEMCACHED_HOST, application_settings.MEMCACHED_PORT)
    FastAPICache.init(
        backend=CustomMemcachedBackend(memcached),
        prefix="fastapi-cache",
        expire=application_settings.CACHE_EXPIRE_TIME,
        enable=application_settings.CACHE_ACTIVE,
    )
    await init_db.init()
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


# @app.on_event("startup")
# def startup():
#     redis_cache = FastApiRedisCache()
#     redis_cache.init(
#         host_url=application_settings.REDIS_URL,
#         prefix="myapi-cache",
#         response_header="X-MyAPI-Cache",
#         ignore_arg_types=[Request, Response, Session]
#     )
