from enum import Enum

from .base import TaskFilter
from .keyword import KeywordTaskFilter
from .regex import RegexTaskFilter
from .views import ViewsTaskFilter
from .responses import ResponsesTaskFilter
from .price import PriceTaskFilter
from .lifetime import LifetimeTaskFilter


class FilterType(Enum):
    KEYWORD = KeywordTaskFilter
    REGEX = RegexTaskFilter
    VIEWS = ViewsTaskFilter
    RESPONSES = ResponsesTaskFilter
    PRICE = PriceTaskFilter
    LIFETIME = LifetimeTaskFilter