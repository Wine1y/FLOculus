import re
import asyncio
from typing import AsyncGenerator, List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from .bs4 import BS4PlatformParser
from ..tasks import FreelanceRuTask, FreelanceRuTaskAuthor, PriceType
from ..tasks.freelance_ru import PaymentType, AuthorPreferences


ID_RE = re.compile(r".+-(?P<id>\d+).html")


class FreelanceRuParser(BS4PlatformParser):
    name: str = "freelance.ru"
    base_url: str = "https://freelance.ru"

    async def parse_tasks(self) -> AsyncGenerator[FreelanceRuTask, None]:
        page = 1
        while True:
            soup = await self._get_page_soup(f"/project/search?q=&a=0&a=1&v=0&c=&page={page}")
            await asyncio.sleep(self.request_delay_seconds)

            for div in soup.select("div.project"):
                path = div.select_one(".title a").attrs.get("href")
                author = FreelanceRuTaskAuthor(
                    name=self._get_tag_text(div.select_one("span.user-name"))
                )
                views_str = self._get_tag_text(div.select_one("span.view-count"))
                responses_str = self._get_tag_text(div.select_one("span.comments-count"))

                tags = [
                    self._get_tag_text(tag)
                    for tag in div.select("div.specs-list>*:not(.more)")
                ]

                preferences = list()
                for i in div.select("div.project-preferences > i"):
                    pref_title = i.attrs.get("title", "").lower()
                    if pref_title in AuthorPreferences:
                        preferences.append(AuthorPreferences(pref_title))

                yield await self._parse_task(
                    path=path,
                    author=author,
                    views=int(views_str) if views_str is not None else 0,
                    responses=int(responses_str) if responses_str is not None else 0,
                    tags=tags, preferences=preferences,
                    raised=div.select_one("span img.up") is not None
                )
                await asyncio.sleep(self.request_delay_seconds)

            if soup.select_one("ul.pagination li.next.disabled") is not None:
                break
            page+=1
    
    async def _parse_task(
        self, path: str, author: FreelanceRuTaskAuthor,
        views: int=0, responses: int=0,
        raised: bool=False,
        tags:Optional[List[str]]=None, preferences:Optional[List[str]]=None,
    ) -> FreelanceRuTask:
        soup = await self._get_page_soup(path)

        proj_info = {
            self._get_tag_text(cells[0]).lower().strip(':'): self._get_tag_text(cells[1]).lower()
            for row in soup.select("div.project_info_block table tr")
            if (cells := row.select("td"))
        }

        price = int(price.replace(' ', '')[:-6]) if (price := proj_info["стоимость"]) != "договорная" else None
        last_seen_str = proj_info.get("был(а) на сайте") or proj_info.get("была на сайте") or proj_info.get("был на сайте")
        author.last_seen_at = datetime.strptime(
            last_seen_str, "%Y-%m-%d %H:%M"
        ).replace(tzinfo=ZoneInfo("Europe/Moscow"))
        posted_at = datetime.strptime(
            proj_info["дата публикации"], "%Y-%m-%d %H:%M"
        ).replace(tzinfo=ZoneInfo("Europe/Moscow"))


        return FreelanceRuTask(
            id=ID_RE.search(path).group("id"),
            title=self._get_tag_text(soup.select_one(".proj_tophead")),
            url=f"{self.base_url}{path}",
            description=self._get_tag_text(soup.select_one("table#proj_table tr:nth-child(2)")),
            views=views,
            responses=responses,
            posted_at=posted_at,
            tags=tags if tags is not None else list(),
            price=price,
            price_type=PriceType.PER_PROJECT if price is not None else PriceType.UNDEFINED,
            author=author,
            raised=raised,
            payment_type=PaymentType(proj_info["варианты оплаты"].replace('\n', ' ')),
            deadline_days=int(proj_info["срок выполнения"].split(' ')[0]),
            author_preferences=preferences if preferences is not None else list()
        )

