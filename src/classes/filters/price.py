from typing import Optional

from aiogram.utils.i18n import gettext as _, lazy_gettext as __

from .base import TaskFilter
from ..tasks import Task, PriceType


PRICE_TYPE_TO_TRANSLATION = {
    PriceType.UNDEFINED: __("Undefined price"),
    PriceType.PER_HOUR: __("Price per hour"),
    PriceType.PER_PROJECT: __("Price per project")
}

class PriceTaskFilter(TaskFilter):
    price_type: PriceType
    min_price: Optional[int]
    max_price: Optional[int]

    def __init__(self, price_type: PriceType, min_price: Optional[int]=None, max_price: Optional[int]=None, is_negative: bool=False):
        super().__init__(is_negative)

        self.price_type = price_type
        self.min_price = min_price
        self.max_price = max_price

    def _filter(self, task: Task) -> bool:
        if task.price is None or task.price_type != self.price_type:
            return True
        
        match (self.min_price, self.max_price):
            case (None, None):
                raise ValueError(f"{self.__class__.__name__} min_price and max_price can't both be None")
            case (None, max_price):
                return task.price <= max_price
            case (min_price, None):
                return task.price >= min_price
            case (min_price, max_price):
                if min_price > max_price:
                    raise ValueError(f"{self.__class__.__name__} min_price can't be greater than max_price")
                return min_price <= task.price <= max_price
        
    def _translated_str(self) -> str:
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
        
        return _("Price filter ({price_type}): {price}").format(
            price_type=PRICE_TYPE_TO_TRANSLATION[self.price_type],
            price=price
        )