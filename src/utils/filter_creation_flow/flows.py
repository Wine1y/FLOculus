import logging
from abc import ABC
from typing import Type, Dict, Any, Optional
from datetime import timedelta

from aiogram.utils.i18n import lazy_gettext as __

from . import stages
from classes import filters, tasks


class InvalidFlowData(Exception):
    ...

log = logging.getLogger(__name__)

class FilterCreationFlow(ABC):
    filter_type: Type[filters.TaskFilter]
    flow_data: Dict[str, Any]
    flow_stages: stages.CreationFlowStage
    current_stage_index: int

    def __init__(self):
        self.flow_data = dict()
        self.current_stage_index = 0

    @property
    def current_stage(self) -> stages.CreationFlowStage:
        return self.flow_stages[self.current_stage_index]
    
    @property
    def is_last_stage(self) -> bool:
        return self.current_stage_index >= len(self.flow_stages)-1
    
    def next_stage(self) -> stages.CreationFlowStage:
        self.current_stage_index+=1
        return self.current_stage
    
    def process_answer(self, answer: Optional[str]) -> None:
        stage = self.current_stage
        if answer is None and stage.required:
            raise stages.InvalidStageAnswer("Answer is required")
        
        self.flow_data[stage.data_key] = None if answer is None else stage.process_answer(answer)
    
    def build_filter(self) -> filters.TaskFilter:
        log.debug(f"Building filter {self.filter_type} with flow data: {self.flow_data}")
        return self.filter_type(**self.flow_data)

class KeywordFilterCreationFlow(FilterCreationFlow):
    filter_type = filters.KeywordTaskFilter
    flow_stages = [
        stages.StringCreationFlowStage("keyword", __("Please, enter filter keyword")),
        stages.BooleanCreationFlowStage("case_sensitive", __("Make filter case-sensitive (Yes/No)?")),
        stages.BooleanCreationFlowStage("is_negative", __("Make filter negative (Yes/No)?"))
    ]

class RegexFilterCreationFlow(FilterCreationFlow):
    filter_type = filters.RegexTaskFilter
    flow_stages = [
        stages.RegexCreationFlowStage("regexp", __("Please, enter filter regex")),
        stages.BooleanCreationFlowStage("is_negative", __("Make filter negative (Yes/No)?"))
    ]

class ViewsFilterCreationFlow(FilterCreationFlow):
    filter_type = filters.ViewsTaskFilter
    flow_stages = [
        stages.IntegerCreationFlowStage("min_views", __("Please, enter min views amount"), min_value=0, required=False),
        stages.IntegerCreationFlowStage("max_views", __("Please, enter max views amount"), min_value=0, required=False),
        stages.BooleanCreationFlowStage("is_negative", __("Make filter negative (Yes/No)?"))
    ]

    def build_filter(self):
        min_views = self.flow_data.get("min_views")
        max_views = self.flow_data.get("max_views")
        if min_views is None and max_views is None:
            raise InvalidFlowData("min_views and max_views can't both be None")
        if (min_views is not None and max_views is not None) and min_views > max_views:
            raise InvalidFlowData("min_views can't be greater than max_views")
        return super().build_filter()

class ResponsesFilterCreationFlow(FilterCreationFlow):
    filter_type = filters.ResponsesTaskFilter
    flow_stages = [
        stages.IntegerCreationFlowStage("min_responses", __("Please, enter min responses amount"), min_value=0, required=False),
        stages.IntegerCreationFlowStage("max_responses", __("Please, enter max responses amount"), min_value=0, required=False),
        stages.BooleanCreationFlowStage("is_negative", __("Make filter negative (Yes/No)?"))
    ]

    def build_filter(self):
        min_responses = self.flow_data.get("min_responses")
        max_responses = self.flow_data.get("max_responses")
        if min_responses is None and max_responses is None:
            raise InvalidFlowData("min_responses and max_responses can't both be None")
        if (min_responses is not None and max_responses is not None) and min_responses > max_responses:
            raise InvalidFlowData("min_responses can't be greater than max_responses")
        return super().build_filter()

class PriceFilterCreationFlow(FilterCreationFlow):
    filter_type = filters.PriceTaskFilter
    flow_stages = [
        stages.EnumCreationFlowStage("price_type", __("Please, enter filter price type"),
            {
                price_type: translation
                for price_type, translation in tasks.PRICE_TYPE_TO_TRANSLATION.items()
                if price_type != tasks.PriceType.UNDEFINED
            }
        ),
        stages.IntegerCreationFlowStage("min_price", __("Please, enter min price ₽"), min_value=0, required=False),
        stages.IntegerCreationFlowStage("max_price", __("Please, enter max price ₽"), min_value=0, required=False),
        stages.BooleanCreationFlowStage("is_negative", __("Make filter negative (Yes/No)?"))
    ]

    def build_filter(self):
        min_price = self.flow_data.get("min_price")
        max_price = self.flow_data.get("max_price")
        if min_price is None and max_price is None:
            raise InvalidFlowData("min_price and max_price can't both be None")
        if (min_price is not None and max_price is not None) and min_price > max_price:
            raise InvalidFlowData("min_price can't be greater than max_price")
        return super().build_filter()

class LifetimeFilterCreationFlow(FilterCreationFlow):
    filter_type = filters.LifetimeTaskFilter
    flow_stages = [
        stages.IntegerCreationFlowStage("min_lifetime", __("Please, enter min lifetime in seconds"), min_value=0, required=False),
        stages.IntegerCreationFlowStage("max_lifetime", __("Please, enter max lifetime in seconds"), min_value=0, required=False),
        stages.BooleanCreationFlowStage("is_negative", __("Make filter negative (Yes/No)?"))
    ]

    def build_filter(self):
        min_lifetime = self.flow_data.get("min_lifetime")
        max_lifetime = self.flow_data.get("max_lifetime")
        if min_lifetime is None and max_lifetime is None:
            raise InvalidFlowData("min_lifetime and max_lifetime can't both be None")
        if (min_lifetime is not None and max_lifetime is not None) and min_lifetime > max_lifetime:
            raise InvalidFlowData("min_lifetime can't be greater than max_lifetime")
        
        if min_lifetime is not None:
            self.flow_data["min_lifetime"] = timedelta(seconds=min_lifetime)
        if max_lifetime is not None:
            self.flow_data["max_lifetime"] = timedelta(seconds=max_lifetime)
        return super().build_filter()