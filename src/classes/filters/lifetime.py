from typing import Optional
from datetime import timedelta, datetime

from .base import TaskFilter
from ..tasks import Task


class LifetimeTaskFilter(TaskFilter):
    min_lifetime: Optional[timedelta]
    max_lifetime: Optional[timedelta]

    def __init__(self, is_negative:bool=False, min_lifetime: Optional[timedelta]=None, max_lifetime: Optional[timedelta]=None):
        super().__init__(is_negative)

        self.min_lifetime = min_lifetime
        self.max_lifetime = max_lifetime

    def _filter(self, task: Task) -> bool:
        if task.posted_at is None:
            return True

        lifetime = datetime.now(task.posted_at.tzinfo)-task.posted_at
        match (self.min_lifetime, self.max_lifetime):
            case (None, None):
                raise ValueError(f"{self.__class__.__name__} min_lifetime and max_lifetime can't both be None")
            case (None, max_lifetime):
                return lifetime <= max_lifetime
            case (min_lifetime, None):
                return lifetime >= min_lifetime
            case (min_lifetime, max_lifetime):
                if min_lifetime > max_lifetime:
                    raise ValueError(f"{self.__class__.__name__} min_lifetime can't be greater than max_lifetime")
                return min_lifetime <= lifetime <= max_lifetime