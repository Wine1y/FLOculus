from typing import List, Optional
from dataclasses import dataclass, field
from datetime import tzinfo

from aiogram.utils.i18n import gettext as _

from .base import Task, TaskAuthor


@dataclass
class HabrTaskAuthor(TaskAuthor):
    completed_tasks: int
    active_tasks: int
    positive_reviews: int
    negative_reviews: int

    def translated_str(self, tz: tzinfo) -> str:
        return f"{super().translated_str(tz)}[+{self.positive_reviews} | -{self.negative_reviews} | ✅{self.completed_tasks} ⚠️{self.active_tasks}]"

@dataclass
class TaskAttachment():
    filename: str
    url: str

@dataclass
class HabrTask(Task):
    attachments: List[TaskAttachment] = field(default_factory=list)
    
    @property
    def posted_at_time_mark(self) -> int:
        return int(self.id)
    
    def metadata_translated_strings(self, tz: tzinfo) -> List[Optional[str]]:
        return [
            _("Files Attached: <b>{files_attached}</b>").format(files_attached=len(self.attachments)) if len(self.attachments) > 0 else None
        ]