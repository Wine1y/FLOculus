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
                    timedelta(seconds=self.min_lifetime_seconds) if self.min_lifetime_seconds is not None else None,
                    timedelta(seconds=self.max_lifetime_seconds) if self.max_lifetime_seconds is not None else None,
                    self.is_negative
                )
    
    @classmethod
    def from_filter(cls, owner_id: int, filter: filters.TaskFilter) -> "FilterEntry":
        match filter.__class__:
            case filters.KeywordTaskFilter:
                return FilterEntry(
                    owner_id=owner_id, filter_type=filters.FilterType.KEYWORD,
                    keyword=filter.keyword, case_sensitive=filter.case_sensitive, is_negative=filter.is_negative
                )
            case filters.RegexTaskFilter:
                return FilterEntry(
                    owner_id=owner_id, filter_type=filters.FilterType.REGEX,
                    regex=filter.regexp.pattern, is_negative=filter.is_negative
                )
            case filters.ViewsTaskFilter:
                return FilterEntry(
                    owner_id=owner_id, filter_type=filters.FilterType.VIEWS,
                    min_views=filter.min_views, max_views=filter.max_views, is_negative=filter.is_negative
                )
            case filters.ResponsesTaskFilter:
                return FilterEntry(
                    owner_id=owner_id, filter_type=filters.FilterType.RESPONSES,
                    min_responses=filter.min_responses, max_responses=filter.max_responses, is_negative=filter.is_negative
                )
            case filters.PriceTaskFilter:
                return FilterEntry(
                    owner_id=owner_id, filter_type=filters.FilterType.PRICE,
                    price_type=filter.price_type, min_price=filter.min_price,
                    max_price=filter.max_price, is_negative=filter.is_negative
                )
            case filters.LifetimeTaskFilter:
                min_lifetime = None if filter.min_lifetime is None else filter.min_lifetime.total_seconds()
                max_lifetime = None if filter.max_lifetime is None else filter.max_lifetime.total_seconds()
                return FilterEntry(
                    owner_id=owner_id, filter_type=filters.FilterType.LIFETIME,
                    min_lifetime_seconds=min_lifetime,
                    max_lifetime_seconds=max_lifetime,
                    is_negative=filter.is_negative
                )