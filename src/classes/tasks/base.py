from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime


class PriceType(Enum):
    UNDEFINED = "Undefined"
    PER_PROJECT = "Per Project"
    PER_HOUR = "Per Hour"

@dataclass
class TaskAuthor(ABC):
    name: str
    
@dataclass
class Task(ABC):
    id: str
    title: str
    description: Optional[str] = field(default=None)
    views: Optional[int] = field(default=None)
    responses: Optional[int] = field(default=None)
    posted_at: Optional[datetime] = field(default=None)
    tags: List[str] = field(default_factory=list)
    price: Optional[int] = field(default=None)
    price_type: PriceType = field(default=PriceType.UNDEFINED)
    author: Optional[TaskAuthor] = field(default=None)

    @property
    @abstractmethod
    def posted_at_time_mark(self) -> int:
        ...