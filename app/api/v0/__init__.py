from fastapi import APIRouter

from .routers.auth_router import router as auth_router
from .routers.url_router import router as url_router
from .routers.user_router import router as user_router

router = APIRouter(prefix='/v0')

router.include_router(url_router, tags=['URL'], prefix="/url")
router.include_router(auth_router, tags=['Auth'], prefix="/auth")
router.include_router(user_router, tags=['User'], prefix="/users")
