from typing import Optional
from dataclasses import dataclass, field

from .base import Task, TaskAuthor


@dataclass
class FlRuTaskAuthor(TaskAuthor):
    positive_reviews: int
    negative_reviews: int

@dataclass
class FlRuTask(Task):
    deadline: Optional[str] = field(default=None)
    safe_deal: bool = field(default=False)
    self_employed_only: bool = field(default=False)
    urgent: bool = field(default=False)
    min_price: Optional[int] = field(default=None)
    max_price: Optional[int] = field(default=None)

    @property
    def posted_at_time_mark(self) -> int:
        return int(self.posted_at.timestamp())