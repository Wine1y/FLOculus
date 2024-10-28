from typing import AsyncGenerator
from abc import ABC, abstractmethod

from ..tasks import Task


class PlatformParser(ABC):
    async def parse_new_tasks(self, last_time_mark: int) -> AsyncGenerator[Task, None]:
        break_if_old = False
        async for task in self._parse_tasks():
            if task.posted_at_time_mark <= last_time_mark:
                if task.raised:
                    continue
                if break_if_old:
                    break
                break_if_old = True
                continue
            break_if_old = False
            yield task

    @abstractmethod
    async def _parse_tasks(self) -> AsyncGenerator[Task, None]:
        ...