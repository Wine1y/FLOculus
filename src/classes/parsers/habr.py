import re
import asyncio
from typing import AsyncGenerator
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from .bs4 import BS4PlatformParser
from ..tasks import HabrTask, HabrTaskAuthor, PriceType
from ..tasks.habr import TaskAttachment


MONTHS = {
    "января": "01",
    "февраля": "02",
    "марта": "03",
    "апреля": "04",
    "мая": "05",
    "июня": "06",
    "июля": "07",
    "августа": "08",
    "сентября": "09",
    "октября": "10",
    "ноября": "11",
    "декабря": "12"
}
PRICE_TYPES = {
    "за проект": PriceType.PER_PROJECT,
    "за час": PriceType.PER_HOUR
}
POSTED_AT_RE = re.compile(r"(?P<day>\d\d) (?P<month>\w+) (?P<year>\d\d\d\d), (?P<hour>\d\d):(?P<minute>\d\d)")


class HabrParser(BS4PlatformParser):
    name: str = "freelance.habr.com"
    base_url: str = "https://freelance.habr.com"

    async def parse_tasks(self) -> AsyncGenerator[HabrTask, None]:
        page, last_page = 1, 100
        while page <= last_page:
            soup = await self._get_page_soup(f"/tasks?page={page}")
            last_page = int(self._get_tag_text(soup.select_one("div.pagination a:nth-last-child(2)")))
            await asyncio.sleep(self.request_delay_seconds)

            for a in soup.select("ul#tasks_list li article div.task__title a"):
                yield (await self._parse_task(a.attrs.get("href")))
                await asyncio.sleep(self.request_delay_seconds)
            page +=1
    
    async def _parse_task(self, path: str) -> HabrTask:
        soup = await self._get_page_soup(path)

        user_stats = {
            self._get_tag_text(row.select_one(".label")).lower(): self._get_tag_text(row.select_one(".value"), separator=' ')
            for row in soup.select("div.user_statistics div.row:not(.divider)")
        }
        user_reviews = user_stats["отзывы исполнителей"].replace(' ', '').split('/')
        author = HabrTaskAuthor(
            name=self._get_tag_text(soup.select_one("div.user_about div.fullname")),
            completed_tasks=int(user_stats["завершенные заказы"]),
            active_tasks=int(user_stats["в поиске исполнителя"]),
            positive_reviews=abs(int(user_reviews[0])),
            negative_reviews=abs(int(user_reviews[1])),
        )

        dt_match = POSTED_AT_RE.match(self._get_tag_text(list(soup.select_one("div.task__meta").strings)[0]))
        if (span := soup.select_one("div.task__finance span.count")) is not None:
            price = int(list(span.strings)[0].replace(' ', '')[:-4])
            price_type = PRICE_TYPES[self._get_tag_text(span.select_one("span.suffix"))]
        else:
            price = None
            price_type = PriceType.UNDEFINED

        return HabrTask(
            id=path.split("/")[-1],
            title=self._get_tag_text(soup.select_one("h2.task__title")).replace("\n", " "),
            url=f"{self.base_url}{path}",
            description=self._get_tag_text(soup.select_one("div.task__description")),
            views=int(self._get_tag_text(soup.select_one("div.task__meta span.count:nth-child(2)"))),
            responses=int(self._get_tag_text(soup.select_one("div.task__meta span.count:nth-child(1)"))),
            posted_at=datetime(
                year=int(dt_match.group("year")), month=int(MONTHS[dt_match.group("month")]), day=int(dt_match.group("day")),
                hour=int(dt_match.group("hour")), minute=int(dt_match.group("minute")), tzinfo=ZoneInfo("Europe/Moscow")
            ),
            tags=[self._get_tag_text(a) for a in soup.select("div.task__tags ul li a")],
            price=price,
            price_type=price_type,
            author=author,
            attachments=[
                TaskAttachment(Path(a.attrs.get("href")).name, a.attrs.get("href"))
                for a in soup.select("ul#files_list li a")
            ]
        )
    

