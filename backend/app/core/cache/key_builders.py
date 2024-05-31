from typing import Optional

from starlette.responses import Response
from starlette.requests import Request
from fastapi_cache import FastAPICache


def short_url_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    if not kwargs["kwargs"].get("slug"):
        raise ValueError("Your endpoint must have a slug key word argument")

    prefix = FastAPICache.get_prefix()
    slug = kwargs["kwargs"]["slug"]

    cache_key = f"{prefix}:{slug}"
    return cache_key
