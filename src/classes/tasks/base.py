from enum import Enum
from dataclasses import dataclass, field
from abc import ABC
from typing import Optional, List
from datetime import datetime


class PriceType(Enum):
    UNDEFINED = "Undefined"
    PER_PROJECT = "Per Project"
    PER_HOUR = "Per Hour"

@dataclass
class Task(ABC):
    title: str
    description: Optional[str] = field(default=None)
    views: Optional[int] = field(default=None)
    responses: Optional[int] = field(default=None)
    posted_at: Optional[datetime] = field(default=None)
    tags: List[str] = field(default_factory=list)
    price: Optional[int] = field(default=None)
    price_type: PriceType = field(default=PriceType.UNDEFINED)