from html import escape
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime, tzinfo

from aiogram.utils.i18n import gettext as _, lazy_gettext as __


class PriceType(Enum):
    UNDEFINED = "Undefined"
    PER_PROJECT = "Per Project"
    PER_HOUR = "Per Hour"

PRICE_TYPE_TO_TRANSLATION = {
    PriceType.UNDEFINED: __("Undefined price"),
    PriceType.PER_HOUR: __("Price per hour"),
    PriceType.PER_PROJECT: __("Price per project")
}

@dataclass
class TaskAuthor(ABC):
    name: Optional[str]

    def translated_str(self, tz: tzinfo) -> str:
        return escape(self.name) if self.name is not None else _("Anonymous author")
    
@dataclass
class Task(ABC):
    id: str
    title: str
    url: str
    description: Optional[str] = field(default=None)
    views: Optional[int] = field(default=None)
    responses: Optional[int] = field(default=None)
    posted_at: Optional[datetime] = field(default=None)
    tags: List[str] = field(default_factory=list)
    price: Optional[int] = field(default=None)
    price_type: PriceType = field(default=PriceType.UNDEFINED)
    author: Optional[TaskAuthor] = field(default=None)
    raised: Optional[bool] = field(default=None)

    @property
    @abstractmethod
    def posted_at_time_mark(self) -> int:
        ...

    @abstractmethod
    def metadata_translated_strings(self, tz: tzinfo) -> List[Optional[str]]:
        ...
    
    def price_translated_str(self) -> str:
        if self.price_type == PriceType.UNDEFINED:
            return str(PRICE_TYPE_TO_TRANSLATION[self.price_type])
        return _("Price: <b>{price}₽ ({price_type})</b>").format(
            price=self.price, price_type=str(PRICE_TYPE_TO_TRANSLATION[self.price_type])
        )

    def translated_str(self, tz: tzinfo) -> str:
        string = f"<b>{escape(self.title)}</b>\n\n"

        if self.description is not None:
            string+=f"{escape(self.description)}\n\n"

        string += f"{self.price_translated_str()}\n"

        views_responses_parts = list()
        if self.views is not None and self.views > 0:
            views_responses_parts.append(_("Views: <b>{views}</b>").format(views=self.views))
        if self.responses is not None and self.responses > 0:
            views_responses_parts.append(_("Responses: <b>{responses}</b>").format(responses=self.responses))
        
        if len(views_responses_parts) > 0:
            string+=f"{', '.join(views_responses_parts)}\n"
        
        metadata = [line for line in self.metadata_translated_strings(tz) if line is not None]
        if len(metadata) > 0:
            string+=f"{'\n'.join(metadata)}\n\n"
        else:
            string+='\n'
        
        if self.author is not None:
            string+=f"{self.author.translated_str(tz)}\n"
        if self.posted_at is not None:
            string+=self.posted_at.astimezone(tz).strftime("%H:%M %d.%m.%y")

        return string