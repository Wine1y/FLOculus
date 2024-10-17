from typing import Optional

from .base import TaskFilter
from ..tasks import Task


class ViewsTaskFilter(TaskFilter):
    min_views: Optional[int]
    max_views: Optional[int]

    def __init__(self, is_negative:bool=False, min_views: Optional[int]=None, max_views: Optional[int]=None):
        super().__init__(is_negative)

        self.min_views = min_views
        self.max_views = max_views

    def _filter(self, task: Task) -> bool:
        if task.views is None:
            return True
        
        match (self.min_views, self.max_views):
            case (None, None):
                raise ValueError(f"{self.__class__.__name__} min_views and max_views can't both be None")
            case (None, max_views):
                return task.views <= max_views
            case (min_views, None):
                return task.views >= min_views
            case (min_views, max_views):
                if min_views > max_views:
                    raise ValueError(f"{self.__class__.__name__} min_views can't be greater than max_views")
                return min_views <= task.views <= max_views