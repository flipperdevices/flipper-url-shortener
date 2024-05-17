from fastapi import APIRouter
from .routers.url_router import router as url_router

router = APIRouter(prefix="/v0")

router.include_router(url_router, tags=["URL"], prefix="/url")
