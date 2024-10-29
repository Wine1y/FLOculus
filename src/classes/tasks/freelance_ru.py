from typing import Optional, List
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field

from .base import Task, TaskAuthor


class PaymentType(Enum):
    BY_AGREEMENT = "по договоренности"
    BY_CONTRACT = "заключение договора"
    SAFE_DEAL = "планируется использовать безопасную сделку"

class AuthorPreferences(Enum):
    VERIFICATED = "паспорт верифицирован"
    SAFE_DEAL = "использовал «безопасную сделку»"
    PREMIUM = "аккаунт PRO"
    CERTIFICATE = "сертификат гильдии фрилансеров"

@dataclass
class FreelanceRuTaskAuthor(TaskAuthor):
    last_seen_at: Optional[datetime] = field(default=None)

@dataclass
class FreelanceRuTask(Task):
    payment_type: PaymentType = field(default=PaymentType.BY_AGREEMENT)
    deadline_days: Optional[int] = field(default=None)
    author_preferences: List[AuthorPreferences] = field(default_factory=list)

    @property
    def posted_at_time_mark(self) -> int:
        return int(self.id)