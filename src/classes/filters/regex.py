import re
from html import escape

from aiogram.utils.i18n import gettext as _

from .base import TaskFilter
from ..tasks import Task


class RegexTaskFilter(TaskFilter):
    regexp: re.Pattern[str]

    def __init__(self, regexp: re.Pattern | str, is_negative: bool=False):
        super().__init__(is_negative)
        self.regexp = re.compile(regexp, re.IGNORECASE) if isinstance(regexp, str) else regexp

    def _filter(self, task: Task) -> bool:
        return any((
            self.regexp.search(task.title) is not None,
            self.regexp.search(task.description or "") is not None,
            any(map(lambda tag: self.regexp.search(tag) is not None, task.tags))
        ))

    def _translated_str(self) -> str:
        return _("Regex filter: <b>«{regex}»</b>").format(regex=escape(self.regexp.pattern))