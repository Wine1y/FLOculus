import logging
from typing import AsyncGenerator
from abc import ABC, abstractmethod

from ..tasks import Task


log = logging.getLogger(__name__)

class PlatformParser(ABC):
    name: str

    async def __aenter__(self) -> "PlatformParser":
        return self

    @abstractmethod
    async def parse_tasks(self) -> AsyncGenerator[Task, None]:
        ...