import logging
from typing import AsyncGenerator
from abc import ABC, abstractmethod

from ..tasks import Task


log = logging.getLogger(__name__)

class PlatformParser(ABC):
    name: str

    async def parse_new_tasks(self, last_time_mark: int) -> AsyncGenerator[Task, None]:
        break_if_old = False
        async for task in self._parse_tasks():
            if task.posted_at_time_mark <= last_time_mark:
                if task.raised:
                    log.debug(f"[{self.name} PARSER] task parsed: {task}. Result: Task is raised and will be skipped without checking break_if_old")
                    continue
                if break_if_old:
                    log.debug(f"[{self.name} PARSER] task parsed: {task}. Result: Task is older than last_time_mark and break_if_old is set, parsing will be stopped")
                    break
                log.debug(f"[{self.name} PARSER] task parsed: {task}. Result: Task is older than last_time_mark, break_if_old will be set")
                break_if_old = True
                continue
            log.debug(f"[{self.name} PARSER] task parsed: {task}. Result: Task is new, it will be yielded, break_if_old will be cleared")
            break_if_old = False
            yield task

    async def __aenter__(self) -> "PlatformParser":
        return self

    @abstractmethod
    async def _parse_tasks(self) -> AsyncGenerator[Task, None]:
        ...