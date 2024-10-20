from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, Text, Boolean, Enum, ForeignKey

from classes.tasks import PriceType
from classes import filters
from ..base import BaseModel
from .user import User


class FilterEntry(BaseModel):
    __tablename__ = "filters"

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped[User] = relationship(back_populates="filters")
    filter_type: Mapped[filters.FilterType] = mapped_column(Enum(filters.FilterType))
    is_negative: Mapped[bool] = mapped_column(Boolean, default=False)
    #KeywordTaskFilter
    case_sensitive: Mapped[Optional[bool]] = mapped_column(Boolean)
    keyword: Mapped[Optional[str]] = mapped_column(Text)
    #RegexTaskFilter
    regex: Mapped[Optional[str]] = mapped_column(Text)
    #ViewsTaskFilter
    min_views: Mapped[Optional[int]] = mapped_column(Integer)
    max_views: Mapped[Optional[int]] = mapped_column(Integer)
    #ResponsesTaskFilter
    min_responses: Mapped[Optional[int]] = mapped_column(Integer)
    max_responses: Mapped[Optional[int]] = mapped_column(Integer)
    #PriceTaskFilter
    price_type: Mapped[Optional[PriceType]] = mapped_column(Enum(PriceType))
    min_price: Mapped[Optional[int]] = mapped_column(Integer)
    max_price: Mapped[Optional[int]] = mapped_column(Integer)
    #LifetimeTaskFilter
    min_lifetime_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    max_lifetime_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    def to_filter(self) -> filters.TaskFilter:
        match self.filter_type:
            case filters.FilterType.KEYWORD:
                return filters.KeywordTaskFilter(self.keyword, self.case_sensitive, self.is_negative)
            case filters.FilterType.REGEX:
                return filters.RegexTaskFilter(self.regex, self.is_negative)
            case filters.FilterType.VIEWS:
                return filters.ViewsTaskFilter(self.min_views, self.max_views, self.is_negative)
            case filters.FilterType.RESPONSES:
                return filters.ResponsesTaskFilter(self.min_responses, self.max_responses, self.is_negative)
            case filters.FilterType.PRICE:
                return filters.PriceTaskFilter(self.price_type, self.min_price, self.max_price, self.is_negative)
            case filters.FilterType.LIFETIME:
                return filters.LifetimeTaskFilter(
                    timedelta(seconds=self.min_lifetime_seconds),
                    timedelta(seconds=self.max_lifetime_seconds),
                    self.is_negative
                )