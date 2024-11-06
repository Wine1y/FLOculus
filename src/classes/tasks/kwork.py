from typing import List, Optional
from datetime import datetime, tzinfo
from dataclasses import dataclass, field

from aiogram.utils.i18n import gettext as _

from .base import Task, TaskAuthor, PriceType, PRICE_TYPE_TO_TRANSLATION


@dataclass
class KworkTaskAuthor(TaskAuthor):
    tasks_posted: int
    hired_percent: int

    def translated_str(self, tz: tzinfo) -> str:
        return f"{super().translated_str(tz)}[💼{self.tasks_posted} 🤝{self.hired_percent}%]"

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
    
    def price_translated_str(self) -> str:
        if self.price is not None or self.price_type == PriceType.UNDEFINED:
            return super().price_translated_str()
        
        price = _("From {min_price}₽ to {max_price}₽").format(
            min_price=self.preffered_max_price, max_price=self.acceptable_max_price
        )
        return _("Price: <b>{price} ({price_type})</b>").format(
            price=price, price_type=PRICE_TYPE_TO_TRANSLATION[self.price_type]
        )

    def metadata_translated_strings(self, tz: tzinfo) -> List[Optional[str]]:
        expire_at = self.expire_at.astimezone(tz).strftime("%H:%H %d.%m") if self.expire_at else None
        return [
            _("Task Expires At: <b>{expire_at}</b>").format(expire_at=expire_at) if expire_at is not None else None,
            _("Files Attached: <b>{files_attached}</b>").format(files_attached=len(self.attachments)) if len(self.attachments) > 0 else None
        ]