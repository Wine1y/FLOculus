from typing import Optional

from aiogram.utils.i18n import gettext as _

from .base import TaskFilter
from ..tasks import Task


class ViewsTaskFilter(TaskFilter):
    min_views: Optional[int]
    max_views: Optional[int]

    def __init__(self, min_views: Optional[int]=None, max_views: Optional[int]=None, is_negative:bool=False):
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
    
    def _translated_str(self) -> str:
        views = None
        match (self.min_views, self.max_views):
            case (None, None):
                raise ValueError(f"{self.__class__.__name__} min_views and max_views can't both be None")
            case (None, max_views):
                views = _("Up to {max_views} view", "Up to {max_views} views", max_views).format(max_views=max_views)
            case (min_views, None):
                views = _("At least {min_views} view", "At least {min_views} views", min_views).format(min_views=min_views)
            case (min_views, max_views):
                views = _("From {min_views} to {max_views} view", "From {min_views} to {max_views} views", max_views).format(min_views=min_views, max_views=max_views)
        
        return _("Views filter: <b>{views}</b>").format(views=views)