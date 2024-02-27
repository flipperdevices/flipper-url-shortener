import hashlib
from typing import Callable, Optional

from fastapi_cache import FastAPICache
from loguru import logger
from starlette.requests import Request
from starlette.responses import Response


def short_url_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    if not kwargs['kwargs'].get('short_url'):
        raise ValueError('Your endpoint must have a short_url key word argument')

    prefix = FastAPICache.get_prefix()
    short_url = kwargs['kwargs']['short_url']

    cache_key = f"{prefix}:{short_url}"
    return cache_key
