from re import Pattern

from .base import TaskFilter
from ..tasks import Task


class RegexTaskFilter(TaskFilter):
    regexp: Pattern[str]

    def __init__(self, regexp: Pattern, is_negative: bool=False):
        super().__init__(is_negative)
        self.regexp = regexp

    def _filter(self, task: Task) -> bool:
        return any((
            self.regexp.search(task.title) is not None,
            self.regexp.search(task.description or "") is not None,
            any(map(lambda tag: self.regexp.search(tag) is not None, task.tags))
        ))