import re
from typing import Any, Optional, Dict, List
from abc import ABC, abstractmethod

from aiogram.utils.i18n import gettext as _
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class InvalidStageAnswer(Exception):
    ...

class CreationFlowStage(ABC):
    data_key: str
    stage_question: str
    required: bool

    def __init__(self, data_key: str, stage_question: str, required: bool=True):
        self.data_key = data_key
        self.stage_question = stage_question
        self.required = required

    @abstractmethod
    def process_answer(self, answer: str) -> Any:
        ...
    
    def get_variants(self) -> List[str]:
        return list()
    
    def get_keyboard(self) -> types.ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()
        if len(variants := self.get_variants()) > 0:
            for variant in variants:
                builder.add(types.KeyboardButton(text=str(variant)))
        if not self.required:
            builder.add(types.KeyboardButton(text=_("Skip")))
        builder.add(types.KeyboardButton(text=_("Cancel")))
        keyboard = builder.as_markup()
        keyboard.resize_keyboard = True
        return keyboard

class BooleanCreationFlowStage(CreationFlowStage):
    def process_answer(self, answer: str) -> bool:
        if answer.lower() == _("Yes").lower():
            return True
        if answer.lower() == _("No").lower():
            return False
        raise InvalidStageAnswer("Answer should be \"yes\" or \"no\"")

    def get_variants(self) -> List[str]:
        return [_("Yes"), _("No")]

class StringCreationFlowStage(CreationFlowStage):
    def process_answer(self, answer: str) -> str:
        return answer

class RegexCreationFlowStage(CreationFlowStage):
    def process_answer(self, answer: str) -> re.Pattern[str]:
        try:
            return re.compile(answer)
        except re.error as e: 
            raise InvalidStageAnswer(f"Invalid regex ({e.msg})")

class IntegerCreationFlowStage(CreationFlowStage):
    min_value: Optional[int]
    max_value: Optional[int]

    def __init__(
        self, data_key: str, stage_question: str,
        min_value: Optional[int]=None, max_value: Optional[int]=None,
        required: bool=True
    ):
        super().__init__(data_key=data_key, stage_question=stage_question, required=required)
        self.min_value = min_value
        self.max_value = max_value

    def process_answer(self, answer: str) -> int:
        try:
            integer = int(answer)
        except ValueError:
            raise InvalidStageAnswer(f"{answer} is not a valid integer")
        
        if self.min_value is not None and integer < self.min_value:
            raise InvalidStageAnswer(f"{integer} have to be greater than min_value ({self.min_value})")
        if self.max_value is not None and integer > self.max_value:
            raise InvalidStageAnswer(f"{integer} have to be less than max_value ({self.max_value})")
        return integer

class EnumCreationFlowStage(CreationFlowStage):
    enum_to_answer: Dict[Any, str]

    def __init__(
        self, data_key: str, stage_question: str, enum_to_answer: Dict[Any, str],
        required: bool = True
    ):
        super().__init__(data_key=data_key, stage_question=stage_question, required=required)
        self.enum_to_answer = enum_to_answer
    
    def process_answer(self, answer: str) -> Any:
        for enum, enum_anser in self.enum_to_answer.items():
            if answer == str(enum_anser):
                return enum
        raise InvalidStageAnswer(f"Invalid enum variant: {answer}")

    def get_variants(self) -> List[str]:
        return [str(answer) for answer in self.enum_to_answer.values()]