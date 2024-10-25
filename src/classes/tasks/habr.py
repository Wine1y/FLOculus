from typing import List
from dataclasses import dataclass, field

from .base import Task, TaskAuthor


@dataclass
class HabrTaskAuthor(TaskAuthor):
    completed_tasks: int
    active_tasks: int
    tasks_in_arbitration: int
    positive_reviews: int
    negative_reviews: int

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