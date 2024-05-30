from functools import lru_cache
from operator import attrgetter
from enum import unique, Enum


@unique
class BaseEnum(Enum):
    @classmethod
    @lru_cache(None)
    def values(cls) -> tuple:
        return tuple(map(attrgetter("value"), cls))
