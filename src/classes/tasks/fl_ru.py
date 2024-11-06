from html import escape
from typing import Optional, List
from dataclasses import dataclass, field
from datetime import tzinfo

from aiogram.utils.i18n import gettext as _

from .base import Task, TaskAuthor, PriceType, PRICE_TYPE_TO_TRANSLATION


@dataclass
class FlRuTaskAuthor(TaskAuthor):
    positive_reviews: int
    negative_reviews: int

    def translated_str(self, tz: tzinfo) -> str:
        return f"{super().translated_str(tz)}[+{self.positive_reviews} | -{self.negative_reviews}]"

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
    
    def price_translated_str(self) -> str:
        if self.price is not None or self.price_type == PriceType.UNDEFINED:
            return super().price_translated_str()
        price = None
        match (self.min_price, self.max_price):
            case (None, None):
                raise ValueError(f"{self.__class__.__name__} min_price and max_price can't both be None")
            case (None, max_price):
                price = _("Up to {max_price}₽").format(max_price=max_price)
            case (min_price, None):
                price = _("At least {min_price}₽").format(min_price=min_price)
            case (min_price, max_price):
                price = _("From {min_price}₽ to {max_price}₽").format(min_price=min_price, max_price=max_price)

        return _("Price: <b>{price} ({price_type})</b>").format(
            price=price, price_type=PRICE_TYPE_TO_TRANSLATION[self.price_type]
        )

    def metadata_translated_strings(self, tz: tzinfo) -> List[Optional[str]]:
        return [
            _("Deadline: <b>{deadline}</b>").format(deadline=escape(self.deadline)) if self.deadline is not None else None,
            _("Safe Deal: <b>{safe_deal}</b>").format(safe_deal=_("Yes") if self.safe_deal else _("No")),
            _("Self-Employed Only: <b>{se_only}</b>").format(se_only=_("Yes") if self.self_employed_only else _("No")),
            _("<b>Urgent Task</b>")if self.urgent else None,
        ]