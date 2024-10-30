from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .base import Task, TaskAuthor


@dataclass
class KworkTaskAuthor(TaskAuthor):
    tasks_posted: int
    hired_percent: int

@dataclass
class TaskAttachment():
    filename: str
    url: str

@dataclass
class KworkTask(Task):
    preffered_max_price: Optional[int] = field(default=None)
    acceptable_max_price: Optional[int] = field(default=None)
    expire_at: Optional[datetime] = field(default=None)
    attachments: List[TaskAttachment] = field(default_factory=list)
    
    @property
    def posted_at_time_mark(self) -> int:
        return int(self.posted_at.timestamp())