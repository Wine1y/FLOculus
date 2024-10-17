from .base import TaskFilter
from ..tasks import Task


class KeywordTaskFilter(TaskFilter):
    keyword: str
    case_sensitive: bool

    def __init__(self, keyword: str, is_negative: bool=False, case_sensitive: bool=False):
        super().__init__(is_negative)
        self.keyword = keyword
        self.case_sensitive = case_sensitive

    def _filter(self, task: Task) -> bool:
        if self.case_sensitive:
            return any((
                self.keyword in task.title,
                self.keyword in (task.description or ""),
                self.keyword in task.tags
            ))
        else:
            keyword = self.keyword.lower()
            title = task.title.lower()
            desc = task.description.lower() if task.description else ""
            tags = map(lambda tag: tag.lower(), task.tags)
            return any((
                keyword in title,
                keyword in desc,
                keyword in tags
            ))