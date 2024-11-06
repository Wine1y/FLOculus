from typing import Optional, List
from enum import Enum
from datetime import datetime, tzinfo
from dataclasses import dataclass, field

from aiogram.utils.i18n import gettext as _, lazy_gettext as __

from .base import Task, TaskAuthor


class PaymentType(Enum):
    BY_AGREEMENT = "по договоренности"
    BY_CONTRACT = "заключение договора"
    SAFE_DEAL = "планируется использовать безопасную сделку"

PAYMENT_TYPE_TO_TRANSLATION = {
    PaymentType.BY_AGREEMENT: __("By Agreement"),
    PaymentType.BY_CONTRACT: __("By Contract"),
    PaymentType.SAFE_DEAL: __("Via Safe Deal")
}

class AuthorPreferences(Enum):
    VERIFICATED = "паспорт верифицирован"
    SAFE_DEAL = "использовал «безопасную сделку»"
    PREMIUM = "аккаунт PRO"
    CERTIFICATE = "сертификат гильдии фрилансеров"

AUTHOR_PREFERENCE_TO_FLAG = {
    AuthorPreferences.VERIFICATED: '✅',
    AuthorPreferences.SAFE_DEAL: '🔐',
    AuthorPreferences.PREMIUM: '👑',
    AuthorPreferences.CERTIFICATE: '🎓'
}

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
    
    def metadata_translated_strings(self, tz: tzinfo) -> List[Optional[str]]:
        deadline_string = None
        if self.deadline_days is not None:
            deadline_string = _(
                "Deadline: <b>{deadline_days} day</b>",
                "Deadline: <b>{deadline_days} days</b>",
                self.deadline_days
            ).format(
                deadline_days=self.deadline_days
            )
        preference_flags = ''.join([AUTHOR_PREFERENCE_TO_FLAG[preference] for preference in self.author_preferences])
        return [
            _("Payment Type: <b>{payment_type}</b>").format(payment_type=PAYMENT_TYPE_TO_TRANSLATION[self.payment_type]),
            deadline_string,
            _("Author Preferences: [{preferences}]").format(preferences=preference_flags) if len(preference_flags) > 0 else None
        ]