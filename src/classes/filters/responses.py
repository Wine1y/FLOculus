from typing import Optional

from aiogram.utils.i18n import gettext as _

from .base import TaskFilter
from ..tasks import Task


class ResponsesTaskFilter(TaskFilter):
    min_responses: Optional[int]
    max_responses: Optional[int]

    def __init__(self, min_responses: Optional[int]=None, max_responses: Optional[int]=None, is_negative:bool=False):
        super().__init__(is_negative)

        self.min_responses = min_responses
        self.max_responses = max_responses

    def _filter(self, task: Task) -> bool:
        if task.responses is None:
            return True
        
        match (self.min_responses, self.max_responses):
            case (None, None):
                raise ValueError(f"{self.__class__.__name__} min_responses and max_responses can't both be None")
            case (None, max_responses):
                return task.responses <= max_responses
            case (min_responses, None):
                return task.responses >= min_responses
            case (min_responses, max_responses):
                if min_responses > max_responses:
                    raise ValueError(f"{self.__class__.__name__} min_responses can't be greater than max_responses")
                return min_responses <= task.responses <= max_responses
    
    def _translated_str(self) -> str:
        responses = None
        match (self.min_responses, self.max_responses):
            case (None, None):
                raise ValueError(f"{self.__class__.__name__} min_responses and max_responses can't both be None")
            case (None, max_responses):
                responses = _("Up to {max_responses} response", "Up to {max_responses} responses", max_responses).format(max_responses=max_responses)
            case (min_responses, None):
                responses = _("At least {min_responses} response", "At least {min_responses} responses", min_responses).format(min_responses=min_responses)
            case (min_responses, max_responses):
                responses = _("From {min_responses} to {max_responses} response", "From {min_responses} to {max_responses} responses", max_responses).format(min_responses=min_responses, max_responses=max_responses)
        
        return _("Responses filter: <b>{responses}</b>").format(responses=responses)