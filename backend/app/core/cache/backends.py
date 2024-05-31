from typing import Optional

from fastapi_cache.backends.memcached import MemcachedBackend


class CustomMemcachedBackend(MemcachedBackend):
    async def clear(
        self, namespace: Optional[str] = None, key: Optional[str] = None
    ) -> int:
        if not key:
            return 0

        return await self.mcache.delete(key.encode())
