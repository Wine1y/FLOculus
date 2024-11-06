from typing import Optional
from datetime import timedelta, datetime

from aiogram.utils.i18n import gettext as _

from .base import TaskFilter
from ..tasks import Task


class LifetimeTaskFilter(TaskFilter):
    min_lifetime: Optional[timedelta]
    max_lifetime: Optional[timedelta]

    def __init__(self, min_lifetime: Optional[timedelta]=None, max_lifetime: Optional[timedelta]=None, is_negative:bool=False):
        super().__init__(is_negative)

        self.min_lifetime = min_lifetime
        self.max_lifetime = max_lifetime

    def _filter(self, task: Task) -> bool:
        if task.posted_at is None:
            return True

        lifetime = datetime.now(task.posted_at.tzinfo)-task.posted_at
        match (self.min_lifetime, self.max_lifetime):
            case (None, None):
                raise ValueError(f"{self.__class__.__name__} min_lifetime and max_lifetime can't both be None")
            case (None, max_lifetime):
                return lifetime <= max_lifetime
            case (min_lifetime, None):
                return lifetime >= min_lifetime
            case (min_lifetime, max_lifetime):
                if min_lifetime > max_lifetime:
                    raise ValueError(f"{self.__class__.__name__} min_lifetime can't be greater than max_lifetime")
                return min_lifetime <= lifetime <= max_lifetime

    def _translated_str(self) -> str:
        lifetime = None
        match (self.min_lifetime, self.max_lifetime):
            case (None, None):
                raise ValueError(f"{self.__class__.__name__} min_lifetime and max_lifetime can't both be None")
            case (None, max_lifetime):
                lifetime = _("Up to {max_lifetime}").format(max_lifetime=_lifetime_to_translated_str(max_lifetime))
            case (min_lifetime, None):
                lifetime = _("At least {min_lifetime}").format(min_lifetime=_lifetime_to_translated_str(max_lifetime))
            case (min_lifetime, max_lifetime):
                if min_lifetime > max_lifetime:
                    raise ValueError(f"{self.__class__.__name__} min_lifetime can't be greater than max_lifetime")
                lifetime = _("From {min_lifetime} to {max_lifetime}").format(min_lifetime=_lifetime_to_translated_str(min_lifetime), max_lifetime=_lifetime_to_translated_str(max_lifetime))
        
        return _("Lifetime filter: <b>{lifetime}</b>").format(lifetime=lifetime)

def _lifetime_to_translated_str(lifetime: timedelta) -> str:
    days, remaining = int(lifetime.total_seconds()//86400), lifetime.total_seconds()%86400
    hours, remaining = int(remaining//3600), remaining%3600
    minutes = int(remaining//60)
    parts = []
    if days > 0:
        parts.append(_("{days} day", "{days} days", days).format(days=days))
    if hours > 0:
        parts.append(_("{hours} hour", "{hours} hours", hours).format(hours=hours))
    if minutes > 0:
        parts.append(_("{minutes} minute", "{minutes} minutes", minutes).format(minutes=minutes))
    return ' '.join(parts)