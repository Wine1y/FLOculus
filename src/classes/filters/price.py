from typing import Optional, Dict, Tuple

from .base import TaskFilter
from ..tasks import Task, PriceType


class PriceTaskFilter(TaskFilter):
    price_type_to_price_limits: Dict[PriceType, Tuple[Optional[int], Optional[int]]]

    def __init__(self, price_type_to_price_limits: Dict[PriceType, Tuple[Optional[int], Optional[int]]], is_negative: bool=False):
        super().__init__(is_negative)

        self.price_type_to_price_limits = price_type_to_price_limits

    def _filter(self, task: Task) -> bool:
        if task.price is None:
            return True
        
        price_limits = self.price_type_to_price_limits.get(task.price_type)
        if price_limits is None:
            raise KeyError(f"No price limits found for price type {task.price_type}")
        
        match price_limits:
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