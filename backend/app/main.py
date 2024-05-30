import os
from contextlib import asynccontextmanager
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi.staticfiles import StaticFiles
from app.api import router as api_router
from app.api.redirect_router import router as redirect_router
from app.core.settings import application_settings
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.responses import RedirectResponse


@asynccontextmanager
async def lifespan(application: FastAPI):
    FastAPICache.init(
        backend=InMemoryBackend(),
        prefix="fastapi-cache",
        enable=application_settings.CACHE_ACTIVE,
        expire=application_settings.CACHE_EXPIRE_TIME,
    )
    yield


app = FastAPI(
    title=application_settings.APP_TITLE,
    debug=application_settings.APP_DEBUG,
    version=application_settings.APP_VERSION,
    openapi_url=application_settings.APP_OPENAPI_URL,
    docs_url="/api/docs",
    lifespan=lifespan,
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:9000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ],
)


@app.get("/admin")
async def admin_trailing_slash():
    return RedirectResponse("/admin/")


app.mount(
    "/admin",
    StaticFiles(
        directory=os.path.join(os.path.dirname(__file__), "../static"), html=True
    ),
    name="static",
)
app.include_router(api_router)
app.include_router(redirect_router)
add_pagination(app)
