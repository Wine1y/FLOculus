from abc import ABC, abstractmethod

from ..tasks import Task


class TaskFilter(ABC):
    is_negative: bool

    def __init__(self, is_negative: bool=False):
        self.is_negative = is_negative

    @abstractmethod
    def _filter(self, task: Task) -> bool:
        ...

    @abstractmethod
    def _translated_str(self) -> str:
        ...

    def filter(self, task: Task) -> bool:
        result = self._filter(task)
        return result if not self.is_negative else (not result)

    def translated_str(self):
        return f"{'❗️' if self.is_negative else ''}{self._translated_str()}"