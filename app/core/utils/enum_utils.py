from enum import Enum, unique
from functools import lru_cache
from operator import attrgetter


@unique
class BaseEnum(Enum):
    @classmethod
    @lru_cache(None)
    def values(cls) -> tuple:
        return tuple(map(attrgetter('value'), cls))


# class TaskStatusEnum(BaseEnum):
#     SUCCEEDED = 'succeeded'
#     FAILED = 'failed'
#     IN_PROGRESS = 'in-progress'
